from typing import List
import os
import pickle
import numpy as np

import faiss
from sentence_transformers import SentenceTransformer

from app.core.database import get_db
from app.core.config import SearchConfig
from app.models.ptfo_tag_merged import PtfoTagMerged
from app.schemas.search_dto import SearchDTO


class SearchService:
    @staticmethod
    def ptfo_search(request: SearchDTO.PtfoSearchReqDTO) -> List[SearchDTO.PtfoSearchRespDTO]:
        """
        포트폴리오(포폴) 검색을 수행하는 함수입니다.
        사용자 입력(요약 및 태그)을 기반으로, 포폴의 텍스트와 태그 유사도를 각각 계산한 후,
        두 유사도를 가중치(alpha, beta)를 사용해 결합하여 최종 점수를 산출합니다.
        그 후, 최종 점수를 기준으로 정렬된 포폴 결과를 SearchDTO.PtfoSearchRespDTO 객체 리스트로 반환합니다.

        동작 과정:
        1. artifacts 디렉토리의 "portfolio_embeddings.pkl" 파일에서 포폴 임베딩과 매핑 정보를 로드합니다.
           - portfolio_embedding_vectors: 각 포폴의 임베딩 벡터 (numpy array, shape: (N, d)).
           - portfolio_records: 각 포폴의 상세 정보 (예: PTFO_SEQNO, PTFO_NM, PTFO_DESC 등).

        2. 데이터베이스에서 tb_ptfo_tag_merged 테이블을 조회하여,
           각 포폴의 태그 목록을 매핑(딕셔너리) 형태로 생성합니다.

        3. 임베딩 모델(SentenceTransformer 'all-MiniLM-L6-v2')을 초기화하여,
           사용자 입력 요약과 태그를 임베딩합니다.

           3-1. 텍스트 유사도 계산 (FAISS 사용):
                - 포폴 임베딩 벡터들을 정규화한 후, FAISS IndexFlatIP (내적 기반 인덱스)를 생성합니다.
                - 사용자 입력 요약을 임베딩하고 정규화하여, 전체 포폴 임베딩과의 내적(유사도)을 계산합니다.
                - 계산된 유사도를 기반으로 각 포폴의 텍스트 유사도 점수를 산출합니다.

           3-2. 태그 유사도 계산 (Top-K 평균 + 벌점 적용):
                - 사용자 요청에 태그가 존재하는 경우, 각 태그를 임베딩하고 정규화합니다.
                - 포폴별 태그 리스트를 임베딩하여 FAISS 인덱스를 구축한 후,
                  사용자 태그 임베딩과의 Top-K 유사도를 계산합니다.
                - 유사도가 임계값(penalty_threshold) 이하일 경우, 벌점(penalty_factor)을 적용하여 감점 처리합니다.
                - 조정된 Top-K 유사도 점수의 평균값을 해당 포폴의 태그 유사도 점수로 사용합니다.

        4. 텍스트 유사도와 태그 유사도에 각각 가중치(alpha, beta)를 부여하여 최종 점수를 산출합니다.

        5. 각 포폴에 대해 텍스트 유사도, 태그 유사도, 최종 점수 및 추가 정보를 포함하는 결과를 생성하고,
           최종 점수를 기준으로 내림차순 정렬한 후, SearchDTO.PtfoSearchRespDTO 객체 리스트로 반환합니다.

        매개변수:
        - request: SearchDTO.PtfoSearchReqDTO 객체
           - 사용자 입력 요약과 선택된 태그 정보를 포함합니다.

        반환값:
        - List[SearchDTO.PtfoSearchRespDTO]:
           - 각 객체는 최종 점수, 텍스트 유사도, 태그 유사도, 포폴 일련번호(PTFO_SEQNO), 포폴명(PTFO_NM),
             포폴 설명(PTFO_DESC), 그리고 해당 포폴에 매핑된 태그 리스트(tag_names)를 포함합니다.
        """
        artifacts_dir = "./artifacts"

        # 1. artifacts에서 포폴 임베딩 & 정보 로딩
        with open(os.path.join(artifacts_dir, "portfolio_embeddings.pkl"), "rb") as f:
            portfolio_artifact = pickle.load(f)
        portfolio_embedding_vectors = portfolio_artifact["embeddings"]  # numpy array, shape (N, d)
        portfolio_records = portfolio_artifact["data"]  # 각 원소: dict {PTFO_SEQNO, PTFO_NM, PTFO_DESC}

        # 2. DB에서 tb_ptfo_tag_merged 테이블 조회하여 각 포폴의 태그 리스트 매핑 생성
        db = next(get_db())
        tag_rows = db.query(PtfoTagMerged).all()
        portfolio_tag_mapping = {}
        for row in tag_rows:
            portfolio_tag_mapping.setdefault(row.PTFO_SEQNO, []).append(row.TAG_NM)

        # 3. 임베딩 모델 초기화 (텍스트 및 태그 모두 동일 모델 사용)
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        #############################
        # 3-1. 텍스트 유사도 계산 (FAISS)
        #############################
        # 포폴 임베딩 정규화
        # norm_portfolio_embedding_vectors = portfolio_embedding_vectors / np.linalg.norm(portfolio_embedding_vectors, axis=1, keepdims=True)
        # d = norm_portfolio_embedding_vectors.shape[1]
        # # index_text: FAISS 인덱스 (내적 기반 – 정규화된 벡터이면 내적=코사인 유사도)
        # index_text = faiss.IndexFlatIP(d)
        # index_text.add(norm_portfolio_embedding_vectors)

        portfolio_index_path = os.path.join(artifacts_dir, "portfolio_index.faiss")
        if not os.path.exists(portfolio_index_path):
            raise FileNotFoundError(f"포폴 텍스트 인덱스가 존재하지 않습니다: {portfolio_index_path}")
        portfolio_index = faiss.read_index(portfolio_index_path)

        # 사용자 입력 요약 임베딩(정규화)
        summary_vector = embedding_model.encode([request.summary], convert_to_numpy=True)
        summary_vector = summary_vector / np.linalg.norm(summary_vector, axis=1, keepdims=True)
        # k_text: 유사도를 계산할 개수. 포폴 전체 개수로 설정.
        k_text = len(portfolio_records)
        """
        D_text: 유사도 점수 (Dintances, 코사인 유사도), I_text: 유사도 순으로 정렬된 인덱스
        e.g.
                D_text = [[0.95, 0.83, 0.74, ...]]
                I_text = [[  3,    0,   12, ...]]
        3번째 포트폴리오가 가장 유사함, 다음은 0번, 12번 ...
        """
        D_text, I_text = portfolio_index.search(summary_vector, k_text)

        # 각 포폴의 텍스트 유사도 점수 배열 생성 (내적 값이 높을수록 유사)
        text_similarity_scores = np.zeros(len(portfolio_records))
        for rank, idx in enumerate(I_text[0]):
            text_similarity_scores[idx] = D_text[0][rank]

        #############################
        # 3-2. 태그 유사도 계산 (Top-K + 벌점)
        #############################
        tag_similarity_scores = []
        top_k = SearchConfig.TAG_TOP_K
        penalty_threshold = SearchConfig.TAG_SIM_THRESHOLD
        penalty_factor = SearchConfig.TAG_PENALTY_FACTOR

        if request.tags:
            query_tag_vectors = embedding_model.encode(request.tags, convert_to_numpy=True)
            query_tag_vectors = query_tag_vectors / np.linalg.norm(query_tag_vectors, axis=1, keepdims=True)
        else:
            query_tag_vectors = np.array([])

        # 태그 유사도 계산 (Top-K 평균 + 벌점 적용)
        for portfolio in portfolio_records:
            ptfo_seqno = portfolio["PTFO_SEQNO"]
            portfolio_tags = portfolio_tag_mapping.get(ptfo_seqno, [])
            # 포폴에 태그가 없거나, 사용자 입력에 태그가 없으면 유사도 계산 불가 -> 0점
            if not portfolio_tags or len(request.tags) == 0:
                tag_similarity_scores.append(0.0)
                continue

            # 태그 임베딩 + 정규화
            portfolio_tag_vectors = embedding_model.encode(portfolio_tags, convert_to_numpy=True)
            portfolio_tag_vectors = portfolio_tag_vectors / np.linalg.norm(portfolio_tag_vectors, axis=1, keepdims=True)
            d_tag = portfolio_tag_vectors.shape[1] # 태그 임베딩의 차원 수

            # FAISS 인덱스 생성 (유사도 검색을 위함)
            index_tag = faiss.IndexFlatIP(d_tag)
            index_tag.add(portfolio_tag_vectors)

            # 사용자 태그별로 유사도 측정
            adjusted_similarities = []
            for qt_emb in query_tag_vectors:
                qt_emb = np.expand_dims(qt_emb, axis=0)
                # D_tag: 태그 유사도 점수 리스트 (Top-K 개수 만큼), _: 유사한 태그의 인덱스는 쓰지 않으므로 버림.
                D_tag, _ = index_tag.search(qt_emb, min(top_k, len(portfolio_tags)))

                # 벌점 적용 - 유사도 점수가 너무 낮으면 감점
                for sim in D_tag[0]:
                    if sim < penalty_threshold:
                        sim -= penalty_factor * (penalty_threshold - sim)
                    adjusted_similarities.append(sim)

            tag_similarity_scores.append(float(np.mean(adjusted_similarities)) if adjusted_similarities else 0.0)

        tag_similarity_scores = np.array(tag_similarity_scores)
        #############################
        # 3-3. 최종 점수 산출 및 정렬
        #############################
        alpha = SearchConfig.ALPHA
        beta = SearchConfig.BETA
        final_scores = alpha * text_similarity_scores + beta * tag_similarity_scores

        results = []
        for i, portfolio in enumerate(portfolio_records):
            results.append(
                SearchDTO.PtfoSearchRespDTO(
                    final_score=float(final_scores[i]),
                    text_score=float(text_similarity_scores[i]),
                    tag_score=float(tag_similarity_scores[i]),
                    ptfo_seqno=portfolio["PTFO_SEQNO"],
                    ptfo_nm=portfolio["PTFO_NM"],
                    ptfo_desc=portfolio["PTFO_DESC"],
                    tag_names=portfolio_tag_mapping.get(portfolio["PTFO_SEQNO"], [])
                )
            )

        # 최종 점수 내림차순 정렬
        return sorted(results, key=lambda x: x.final_score, reverse=True)