import re
import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer

from app.models.tag_info import TagInfo
from app.models.ptfo_info import PtfoInfo
from app.core.database import SessionLocal
from app.preprocess.text_cleaner import TextCleaner

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# KOREAN_STOPWORDS = {
#     "그리고", "그런데", "그래서", "하지만", "또한", "즉", "이런", "저런", "합니다", "한다", "이다",
#     "있는", "없는", "하는", "것", "등", "및", "같은", "때문에", "위해", "경우", "동안", "으로", "에서"
# }
#
# # 전처리 함수: 소문자 변환, 특수문자 제거, 다중 공백 정리
# def preprocess_text(text: str) -> str:
#     # 1. 소문자 변환 + 특수문자 제거 + 다중 공백 제거
#     text = text.lower()
#     text = re.sub(r"[^가-힣a-zA-Z0-9\s]", " ", text)
#     text = re.sub(r"\s+", " ", text).strip()
#
#     # 2. 불용어 제거
#     tokens = text.split()
#     tokens = [t for t in tokens if t not in KOREAN_STOPWORDS]
#
#     return " ".join(tokens)


def build_faiss_indices():
    # 임베딩 모델 초기화 (예: all-MiniLM-L6-v2)
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    cleaner = TextCleaner()

    # DB에서 데이터 로드
    db = next(get_db())

    # 1. tb_tag_info: 태그명 전처리 (TAG_NM만 사용)
    tags = db.query(TagInfo).all()
    tag_texts = [cleaner.clean(tag.TAG_NM) for tag in tags if tag.TAG_NM]

    # 2. tb_ptfo_info: 포폴명과 포폴설명을 결합 후 전처리
    """
    [03.03.2025 변경사항]
    
    all-MiniLM-L6-v2는 BERT 기반의 sentence-level semantic embedding 을 위해 훈련된 모델으로, 주로 전체 문장의 의미를 벡터로 표현하려는 목적이다.
    
    이 모델은 단어 단위나 문법적 구조보다는 "전체 문장이 어떤 의미를 전달하는가" 를 학습하며,
    
    `제목: ~, 설명: ~` 같은 템플릿은, 서로 다른 정보가 있음을 모델에게 명시적으로 알려주는 힌트가 된다.
    
    "제목"에 해당하는 단어가 앞에 오는 걸 반복적으로 학습하고, "설명"에는 길고 설명적인 문장이 따라오는 것을 익히게 된다.
    
    -> 결과적으로 제목이 중요한 요소라는 걸 간접적으로 반영할 수 있다.
    
    + 기존 preprocess_text 는 모듈화 하여 text_cleaner 로 이전 및 불용어 처리 로직 추가. 
    """
    # portfolio_texts = [
    #     preprocess_text(f"{ptfo.PTFO_NM} {ptfo.PTFO_DESC}")
    #     for ptfo in portfolios if ptfo.PTFO_NM and ptfo.PTFO_DESC
    # ]
    portfolios = db.query(PtfoInfo).all()

    portfolio_texts = [
        cleaner.clean(f"제목: {ptfo.PTFO_NM}. 설명: {ptfo.PTFO_DESC}")
        for ptfo in portfolios if ptfo.PTFO_NM and ptfo.PTFO_DESC
    ]

    # 3. 임베딩 생성
    tag_embeddings = embedding_model.encode(tag_texts, convert_to_numpy=True)
    portfolio_embeddings = embedding_model.encode(portfolio_texts, convert_to_numpy=True)

    # 4. FAISS 인덱스 구축
    # 태그 인덱스 (벡터 차원에 맞게 IndexFlatL2 사용)
    d_tag = tag_embeddings.shape[1]
    tag_index = faiss.IndexFlatL2(d_tag)
    tag_index.add(tag_embeddings)

    # 포폴 인덱스
    d_port = portfolio_embeddings.shape[1]
    portfolio_index = faiss.IndexFlatL2(d_port)
    portfolio_index.add(portfolio_embeddings)

    # 5. DB 레코드의 추가 정보를 포함한 매핑 artifact 생성
    tag_artifact = {
        "embeddings": tag_embeddings,
        "data": [
            {"TAG_SEQNO": tag.TAG_SEQNO, "TAG_NM": tag.TAG_NM}
            for tag in tags if tag.TAG_NM
        ]
    }
    portfolio_artifact = {
        "embeddings": portfolio_embeddings,
        "data": [
            {"PTFO_SEQNO": ptfo.PTFO_SEQNO, "PTFO_NM": ptfo.PTFO_NM, "PTFO_DESC": ptfo.PTFO_DESC}
            for ptfo in portfolios if ptfo.PTFO_NM and ptfo.PTFO_DESC
        ]
    }

    # 6. artifacts 폴더에 pickle 파일로 저장
    artifacts_dir = "../../artifacts"
    os.makedirs(artifacts_dir, exist_ok=True)
    with open(os.path.join(artifacts_dir, "tag_embeddings.pkl"), "wb") as f:
        pickle.dump(tag_artifact, f)
    with open(os.path.join(artifacts_dir, "portfolio_embeddings.pkl"), "wb") as f:
        pickle.dump(portfolio_artifact, f)

    return tag_index, portfolio_index, tag_artifact, portfolio_artifact





if __name__ == "__main__":
    tag_index, portfolio_index, tag_texts, portfolio_texts = build_faiss_indices()
    print("태그 FAISS 인덱스 벡터 개수:", tag_index.ntotal)
    print("포폴 FAISS 인덱스 벡터 개수:", portfolio_index.ntotal)

