import os
import time
from collections import deque
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
from app.services.v3.portfolio_service import PortFolioServiceV3
from app.utils.log_utils import get_logger

logger = get_logger("generate_fused_embeddings_v3")

FACTOR_ORDER = ["full", "desc", "what", "how", "style"]


def _l2norm(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    return x / (norms + eps)


class RateLimiter:
    """
    분당 요청 한도를 지키기 위한 간단한 레이트 리미터 (싱글스레드용).
    - 최근 60초 내 호출 타임스탬프를 관리하고 한도를 초과하면 대기
    """
    def __init__(self, rpm: int):
        self.rpm = max(1, int(rpm))
        self.window = deque()  # 최근 호출 시각(초) 큐

    def wait(self):
        now = time.time()
        # 60초 윈도우 밖의 기록 제거
        while self.window and now - self.window[0] > 60.0:
            self.window.popleft()

        if len(self.window) >= self.rpm:
            # 가장 오래된 호출과의 차이를 기준으로 남은 시간만큼 대기
            sleep_for = 60.0 - (now - self.window[0]) + 0.01
            if sleep_for > 0:
                logger.info(f"[RateLimiter] RPM 한도 도달. {sleep_for:.2f}s 대기")
                time.sleep(sleep_for)
            # 대기 후 창을 다시 정리
            now = time.time()
            while self.window and now - self.window[0] > 60.0:
                self.window.popleft()

        # 이번 호출 기록
        self.window.append(time.time())


def build_fused_faiss_indices_v3():
    """
    factor별 임베딩을 만들고, √가중치로 스케일한 뒤 CONCAT하여 단일(fused) 인덱스를 생성.
    또한 factor별 임베딩/메타를 함께 저장하여 온라인에서 component score 및 메타 노출에 사용.
    """
    db = next(get_db())
    data_list = PortFolioServiceV3.load_portfolio_data(db)

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

    # --- 레이트 리미터 설정 (LLM 호출 전용) ---
    rpm = int(getattr(ModelConfig, "LLM_RPM",
              getattr(ModelConfig, "GEMINI_API_REQUESTS_PER_MINUTE", 60)))
    limiter = RateLimiter(rpm=rpm)
    logger.info(f"[RateLimiter] 활성화: {rpm} req/min")

    factor_texts = {f: [] for f in FACTOR_ORDER}
    records = []

    for idx, data in enumerate(data_list, start=1):
        # 메타 필드
        view_url    = data.get("VIEW_LNK_URL")
        studio_name = data.get("PRDN_STDO_NM")
        prod_cost   = data.get("PRDN_COST")
        prod_period = data.get("PRDN_PERD")

        # ---- LLM 호출 전 RPM 대기 ----
        limiter.wait()

        input_text = f"제목: {data['PTFO_NM']}. 설명: {data['PTFO_DESC']}. 태그: {', '.join(data['tags'])}"
        factors = ad_element_extractor_service_single_ton.extract_elements(
            AdElementDTOV2.AdElementRequest(user_prompt=input_text)
        )
        logger.info(f"[elements] {idx}/{len(data_list)} seq={data['PTFO_SEQNO']} -> "
                    f"desc='{factors.desc}', what='{factors.what}', how='{factors.how}', style='{factors.style}'")

        # 개별 factor 텍스트
        for f in ["desc", "what", "how", "style"]:
            factor_texts[f].append(cleaner.clean(getattr(factors, f, "") or ""))

        full_text = f"desc: {factors.desc}. what: {factors.what}. how: {factors.how}. style: {factors.style}"
        factor_texts["full"].append(cleaner.clean(full_text))

        # artifacts에 저장할 레코드
        records.append({
            "PTFO_SEQNO":   data["PTFO_SEQNO"],
            "PTFO_NM":      data["PTFO_NM"],
            "PTFO_DESC":    data["PTFO_DESC"],
            "tags":         data["tags"],
            "full":         factor_texts["full"][-1],
            "desc":         factor_texts["desc"][-1],
            "what":         factor_texts["what"][-1],
            "how":          factor_texts["how"][-1],
            "style":        factor_texts["style"][-1],
            # 추가 메타
            "VIEW_LNK_URL": view_url,
            "PRDN_STDO_NM": studio_name,
            "PRDN_COST":    prod_cost,
            "PRDN_PERD":    prod_period,
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

        embs = _l2norm(np.ascontiguousarray(embs))
        factor_embs[f] = embs

        with open(os.path.join(artifacts_dir, f"{f}_embeddings.pkl"), "wb") as pf:
            pickle.dump({"embeddings": embs, "data": records}, pf)

        idx = faiss.IndexFlatIP(embs.shape[1])
        idx.add(embs)
        faiss.write_index(idx, os.path.join(artifacts_dir, f"{f}_index.faiss"))
        logger.info(f"[V3-FUSED] {f} index ntotal={idx.ntotal}")

    # √가중치 스케일 + CONCAT → fused 임베딩
    scaled = [factor_embs[f] * sqrt_w[f] for f in FACTOR_ORDER]
    fused = np.concatenate(scaled, axis=1).astype(np.float32)

    # fused 인덱스 저장
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