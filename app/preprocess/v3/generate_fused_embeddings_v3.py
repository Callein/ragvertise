import os
import pickle
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer
import fasttext

from app.core.database import get_db
from app.core.config import ModelConfig, SearchConfig
from app.preprocess.text_cleaner import TextCleaner
from app.schemas.v2.ad_element_extractor_dto import AdElementDTOV2
from app.services.v2.ad_element_extractor_service import ad_element_extractor_service_single_ton
from app.services.v2.portfolio_service import PortFolioServiceV2
from app.utils.log_utils import get_logger

logger = get_logger("generate_fused_embeddings_v3")

FACTOR_ORDER = ["full", "desc", "what", "how", "style"]

def _l2norm(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    return x / (norms + eps)

def build_fused_faiss_indices_v3():
    """
    factor별 임베딩을 만들고, √가중치로 스케일한 뒤 CONCAT하여 단일(fused) 인덱스를 생성.
    또한 기존 factor별 임베딩/메타도 그대로 저장하여, 온라인에서 factor별 스코어 계산에 사용.
    """
    db = next(get_db())
    data_list = PortFolioServiceV2.load_portfolio_data(db)

    embedding_model = SentenceTransformer(ModelConfig.EMBEDDING_MODEL)
    ft = fasttext.load_model(ModelConfig.WORD_EMBEDDING_MODEL_PATH)
    cleaner = TextCleaner()

    # 가중치 및 √가중치
    weights = {
        "full":  float(SearchConfig.FULL_WEIGHT),
        "desc":  float(SearchConfig.DESC_WEIGHT),
        "what":  float(SearchConfig.WHAT_WEIGHT),
        "how":   float(SearchConfig.HOW_WEIGHT),
        "style": float(SearchConfig.STYLE_WEIGHT),
    }
    sqrt_w = {k: np.sqrt(v).astype(np.float32) for k, v in weights.items()}

    factor_texts = {f: [] for f in FACTOR_ORDER}
    records = []

    for data in data_list:
        input_text = f"제목: {data['PTFO_NM']}. 설명: {data['PTFO_DESC']}. 태그: {', '.join(data['tags'])}"
        factors = ad_element_extractor_service_single_ton.extract_elements(
            AdElementDTOV2.AdElementRequest(user_prompt=input_text)
        )

        # 개별 factor 텍스트
        for f in ["desc", "what", "how", "style"]:
            factor_texts[f].append(cleaner.clean(getattr(factors, f, "") or ""))

        full_text = f"desc: {factors.desc}. what: {factors.what}. how: {factors.how}. style: {factors.style}"
        factor_texts["full"].append(cleaner.clean(full_text))

        records.append({
            "PTFO_SEQNO": data["PTFO_SEQNO"],
            "PTFO_NM": data["PTFO_NM"],
            "PTFO_DESC": data["PTFO_DESC"],
            "tags": data["tags"],
            "full": factor_texts["full"][-1],
            "desc": factor_texts["desc"][-1],
            "what": factor_texts["what"][-1],
            "how": factor_texts["how"][-1],
            "style": factor_texts["style"][-1],
        })

    artifacts_dir = f"../../../artifacts/v3/{ModelConfig.EMBEDDING_MODEL}"
    os.makedirs(artifacts_dir, exist_ok=True)

    # factor별 임베딩 생성/정규화
    factor_embs = {}
    for f in FACTOR_ORDER:
        texts = factor_texts[f]
        logger.info(f"[V3-FUSED] {f} 임베딩 생성 (n={len(texts)})")
        if f == "what":
            embs = []
            for t in texts:
                words = (t or "").split()
                if words:
                    mat = np.stack([ft.get_word_vector(w) for w in words], axis=0).astype(np.float32)
                    embs.append(mat.mean(axis=0))
                else:
                    embs.append(np.zeros(ft.get_dimension(), dtype=np.float32))
            embs = np.stack(embs, axis=0).astype(np.float32)
        else:
            embs = embedding_model.encode(texts, convert_to_numpy=True).astype(np.float32)

        embs = _l2norm(np.ascontiguousarray(embs))  # L2 정규화 (직선 거리 기반 단위벡터화)
        factor_embs[f] = embs

        with open(os.path.join(artifacts_dir, f"{f}_embeddings.pkl"), "wb") as pf:
            pickle.dump({"embeddings": embs, "data": records}, pf)

        idx = faiss.IndexFlatIP(embs.shape[1])
        idx.add(embs)
        faiss.write_index(idx, os.path.join(artifacts_dir, f"{f}_index.faiss"))
        logger.info(f"[V3-FUSED] {f} index ntotal={idx.ntotal}")

    # √가중치 스케일 + CONCAT → fused 임베딩
    scaled = [factor_embs[f] * sqrt_w[f] for f in FACTOR_ORDER]  # 각 (N, d_f)
    fused = np.concatenate(scaled, axis=1).astype(np.float32)    # (N, sum d_f)

    fused_index = faiss.IndexFlatIP(fused.shape[1])
    fused_index.add(fused)
    faiss.write_index(fused_index, os.path.join(artifacts_dir, "fused_index.faiss"))

    with open(os.path.join(artifacts_dir, "fused_embeddings.pkl"), "wb") as fp:
        pickle.dump({
            "embeddings": fused,
            "data": records,
            "factor_dims": {f: factor_embs[f].shape[1] for f in FACTOR_ORDER},
            "factor_order": FACTOR_ORDER,
            "weights": weights,
        }, fp)

    logger.info("[V3-FUSED] 모든 인덱스/임베딩 저장 완료.")


if __name__ == "__main__":
    build_fused_faiss_indices_v3()