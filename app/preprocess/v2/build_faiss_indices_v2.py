import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import fasttext

from app.core.database import get_db
from app.core.config import ModelConfig
from app.models.ptfo_tag_merged import PtfoTagMerged
from app.preprocess.text_cleaner import TextCleaner
from app.schemas.v2.ad_element_extractor_dto import AdElementDTOV2
from app.services.v2.ad_element_extractor_service import ad_element_extractor_service_single_ton
from app.services.v2.portfolio_service import PortFolioServiceV2
from app.utils.log_utils import get_logger

logger = get_logger("generate_embedding_v2")


def build_faiss_indices_v2():
    """
    광고 포트폴리오 데이터를 기반으로 factor별 임베딩을 생성하고,
    FAISS 인덱스를 구축하여 artifacts 디렉토리에 저장하는 함수.

    사용되는 factor:
        - full: 전체 문서 기반 통합 텍스트
        - desc: 간략한 설명
        - what: 광고 제품/서비스의 핵심 키워드 (FastText 사용)
        - how: 광고의 방식/도구
        - style: 광고 톤/스타일

    embedding 방식:
        - SBERT: full, desc, how, style
        - FastText: what

    결과:
        - 각 factor별로 FAISS 인덱스 및 벡터(pkl) 저장
    """

    db = next(get_db())
    data_list = PortFolioServiceV2.load_portfolio_data(db)

    embedding_model = SentenceTransformer(ModelConfig.EMBEDDING_MODEL)

    # fastText 모델 로드
    fasttext_model = fasttext.load_model(ModelConfig.WORD_EMBEDDING_MODEL_PATH)

    cleaner = TextCleaner()

    factor_texts = {factor: [] for factor in ["full", "desc", "what", "how", "style"]}
    records = []

    for data in data_list:
        input_text = f"제목: {data['PTFO_NM']}. 설명: {data['PTFO_DESC']}. 태그: {', '.join(data['tags'])}"
        factors = ad_element_extractor_service_single_ton.extract_elements(
            AdElementDTOV2.AdElementRequest(user_prompt=input_text)
        )

        # 각 factor 텍스트 전처리
        for factor_name in ["desc", "what", "how", "style"]:
            clean_text = cleaner.clean(getattr(factors, factor_name, ""))
            factor_texts[factor_name].append(clean_text)

        # full 텍스트 생성
        full_text = f"desc: {factors.desc}. what: {factors.what}. how: {factors.how}. style: {factors.style}"
        clean_full_text = cleaner.clean(full_text)
        factor_texts["full"].append(clean_full_text)

        # 기록
        records.append({
            "PTFO_SEQNO": data["PTFO_SEQNO"],
            "PTFO_NM": data["PTFO_NM"],
            "PTFO_DESC": data["PTFO_DESC"],
            "tags": data["tags"],
            "full": factors.desc,
            "desc": factors.desc,
            "what": factors.what,
            "how": factors.how,
            "style": factors.style
        })

    # FAISS 인덱스 빌드
    artifacts_dir = f"../../../artifacts/v2/{ModelConfig.EMBEDDING_MODEL}"
    os.makedirs(artifacts_dir, exist_ok=True)

    for factor, texts in factor_texts.items():
        logger.info(f"[V2] {factor} factor - 임베딩 시작 (text 개수: {len(texts)})")
        if factor == "what":
            embeddings = []
            for text in texts:
                words = text.split()
                word_vecs = [fasttext_model.get_word_vector(word) for word in words]
                if word_vecs:
                    avg_vec = np.mean(word_vecs, axis=0)
                else:
                    avg_vec = np.zeros(fasttext_model.get_dimension(), dtype=np.float32)
                embeddings.append(avg_vec)
            embeddings = np.array(embeddings, dtype=np.float32)
        else:
            embeddings = embedding_model.encode(texts, convert_to_numpy=True).astype(np.float32)

        # 정규화 및 contiguous
        embeddings = np.ascontiguousarray(embeddings)
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        # FAISS 인덱스
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)

        # 결과 저장
        artifact = {
            "embeddings": embeddings,
            "data": records
        }
        with open(os.path.join(artifacts_dir, f"{factor}_embeddings.pkl"), "wb") as f:
            pickle.dump(artifact, f)
        faiss.write_index(index, os.path.join(artifacts_dir, f"{factor}_index.faiss"))
        logger.info(f"[V2] {factor} factor - 벡터 개수: {index.ntotal}")

    logger.info("[V2] 모든 factor 인덱스/임베딩 저장 완료.")


if __name__ == "__main__":
    build_faiss_indices_v2()