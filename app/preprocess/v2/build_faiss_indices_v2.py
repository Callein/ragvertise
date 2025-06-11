import os
import pickle
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer

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
    db = next(get_db())
    data_list = PortFolioServiceV2.load_portfolio_data(db)

    embedding_model = SentenceTransformer(ModelConfig.EMBEDDING_MODEL)
    cleaner = TextCleaner()

    factor_texts = {
        "desc": [],
        "what": [],
        "how": [],
        "style": []
    }
    records = []

    for data in data_list:
        input_text = f"제목: {data['PTFO_NM']}. 설명: {data['PTFO_DESC']}. 태그: {', '.join(data['tags'])}"
        factors = ad_element_extractor_service_single_ton.extract_elements(
            AdElementDTOV2.AdElementRequest(user_prompt=input_text)
        )

        # 전처리 후 저장
        for factor_name in factor_texts.keys():
            # 수정된 부분: getattr()으로 Pydantic 모델에서 속성 가져오기
            clean_text = cleaner.clean(getattr(factors, factor_name, ""))
            factor_texts[factor_name].append(clean_text)

        records.append({
            "PTFO_SEQNO": data["PTFO_SEQNO"],
            "PTFO_NM": data["PTFO_NM"],
            "PTFO_DESC": data["PTFO_DESC"],
            "tags": data["tags"],
            "desc": factors.desc,
            "what": factors.what,
            "how": factors.how,
            "style": factors.style
        })

    # factor별 임베딩 및 FAISS 인덱스
    artifacts_dir = f"../../../artifacts/v2/{ModelConfig.EMBEDDING_MODEL}"
    os.makedirs(artifacts_dir, exist_ok=True)

    for factor, texts in factor_texts.items():
        embeddings = embedding_model.encode(texts, convert_to_numpy=True)
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)

        # artifacts 저장
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