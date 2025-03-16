from typing import List
import os
import pickle
import numpy as np

import faiss
from sentence_transformers import SentenceTransformer

from util.database import get_db
from model.ptfo_tag_merged import PtfoTagMerged
from schema.search_dto import SearchDTO


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
           - portfolio_embeddings: 각 포폴의 임베딩 벡터 (numpy array, shape: (N, d)).
           - portfolio_data: 각 포폴의 상세 정보 (예: PTFO_SEQNO, PTFO_NM, PTFO_DESC 등).

        2. 데이터베이스에서 tb_ptfo_tag_merged 테이블을 조회하여,
           각 포폴의 태그 목록을 매핑(딕셔너리) 형태로 생성합니다.

        3. 임베딩 모델(SentenceTransformer 'all-MiniLM-L6-v2')을 초기화하여,
           사용자 입력 요약과 태그를 임베딩합니다.

           3-1. 텍스트 유사도 계산 (FAISS 사용):
                - 포폴 임베딩 벡터들을 정규화한 후, FAISS IndexFlatIP (내적 기반 인덱스)를 생성합니다.
                - 사용자 입력 요약을 임베딩하고 정규화하여, 전체 포폴 임베딩과의 내적(유사도)을 계산합니다.
                - 계산된 유사도를 기반으로 각 포폴의 텍스트 유사도 점수를 산출합니다.

           3-2. 태그 유사도 계산 (포폴별 FAISS 사용):
                - 사용자 요청에 태그가 존재하는 경우, 해당 태그들을 임베딩하고 정규화합니다.
                - 각 포폴의 태그 리스트를 임베딩하여 FAISS 인덱스를 생성하고,
                  각 사용자 태그와 포폴 태그 간 최고 유사도를 계산합니다.
                - 임계값 이하의 유사도에는 벌점(penalty_factor)을 적용하여 조정한 후,
                  평균 유사도를 산출해 각 포폴의 태그 유사도 점수를 결정합니다.

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

        # 1. pickle 파일에서 포폴 임베딩 및 매핑 정보 로드
        with open(os.path.join(artifacts_dir, "portfolio_embeddings.pkl"), "rb") as f:
            portfolio_artifact = pickle.load(f)
        portfolio_embeddings = portfolio_artifact["embeddings"]  # numpy array, shape (N, d)
        portfolio_data = portfolio_artifact["data"]  # 각 원소: dict {PTFO_SEQNO, PTFO_NM, PTFO_DESC}

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
        norm_portfolio_embeddings = portfolio_embeddings / np.linalg.norm(portfolio_embeddings, axis=1, keepdims=True)
        d = norm_portfolio_embeddings.shape[1]
        # FAISS 인덱스 (내적 기반 – 정규화된 벡터이면 내적=코사인 유사도)
        index_text = faiss.IndexFlatIP(d)
        index_text.add(norm_portfolio_embeddings)
        # 사용자 입력 요약 임베딩(정규화)
        summary_embedding = embedding_model.encode([request.summary], convert_to_numpy=True)
        summary_embedding = summary_embedding / np.linalg.norm(summary_embedding, axis=1, keepdims=True)
        # 전체 포폴에 대해 k = 전체 개수 검색
        k_text = len(portfolio_data)
        D_text, I_text = index_text.search(summary_embedding, k_text)
        # 각 포폴의 텍스트 유사도 점수 배열 생성 (내적 값이 높을수록 유사)
        text_similarities = np.zeros(len(portfolio_data))
        for rank, idx in enumerate(I_text[0]):
            text_similarities[idx] = D_text[0][rank]

        #############################
        # 3-2. 태그 유사도 계산 (각 포폴별로 FAISS 사용)
        #############################
        if request.tags:
            query_tag_embeddings = embedding_model.encode(request.tags, convert_to_numpy=True)
            query_tag_embeddings = query_tag_embeddings / np.linalg.norm(query_tag_embeddings, axis=1, keepdims=True)
        else:
            query_tag_embeddings = np.array([])

        # 벌점 적용 파라미터, 임계값 이하이면 factor 만큼 가중 벌점 적용
        penalty_threshold = 0.5
        penalty_factor = 3.0

        tag_scores = []
        for portfolio in portfolio_data:
            ptfo_seqno = portfolio["PTFO_SEQNO"]
            portfolio_tags = portfolio_tag_mapping.get(ptfo_seqno, [])
            if not portfolio_tags or len(request.tags) == 0:
                tag_score = 0.0
            else:
                portfolio_tag_emb = embedding_model.encode(portfolio_tags, convert_to_numpy=True)
                portfolio_tag_emb = portfolio_tag_emb / np.linalg.norm(portfolio_tag_emb, axis=1, keepdims=True)
                d_tag = portfolio_tag_emb.shape[1]
                index_tag = faiss.IndexFlatIP(d_tag)
                index_tag.add(portfolio_tag_emb)
                sims = []
                for qt_emb in query_tag_embeddings:
                    qt_emb = np.expand_dims(qt_emb, axis=0)
                    D_tag, _ = index_tag.search(qt_emb, 1)  # k=1: 각 query tag 당 최고 유사도
                    sim = D_tag[0][0]
                    # 벌점 적용: 임계값 미만이면 벌점 차감
                    if sim < penalty_threshold:
                        sim_adjusted = sim - penalty_factor * (penalty_threshold - sim)
                    else:
                        sim_adjusted = sim
                    sims.append(sim_adjusted)
                tag_score = float(np.mean(sims))
            tag_scores.append(tag_score)
        tag_scores = np.array(tag_scores)

        #############################
        # 3-3. 최종 점수 산출 및 정렬
        #############################
        alpha = 0.5
        beta = 0.5
        final_scores = alpha * text_similarities + beta * tag_scores

        results = []
        for i, portfolio in enumerate(portfolio_data):
            res = portfolio.copy()
            res["text_score"] = float(text_similarities[i])
            res["tag_score"] = float(tag_scores[i])
            res["final_score"] = float(final_scores[i])
            res["tags"] = portfolio_tag_mapping.get(portfolio["PTFO_SEQNO"], [])
            results.append(res)

        # 최종 점수 내림차순 정렬
        results_sorted = sorted(results, key=lambda x: x["final_score"], reverse=True)

        ret: List[SearchDTO.PtfoSearchRespDTO] = []
        for res in results_sorted:
            ret.append(SearchDTO.PtfoSearchRespDTO(
                final_score=res["final_score"],
                text_score=res["text_score"],
                tag_score=res["tag_score"],
                ptfo_seqno=res["PTFO_SEQNO"],
                ptfo_nm=res["PTFO_NM"],
                ptfo_desc=res["PTFO_DESC"],
                tag_names=res["tags"]
            ))
        return ret