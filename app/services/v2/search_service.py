from typing import List
import os
import pickle
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer
import fasttext
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import SearchConfig, ModelConfig
from app.schemas.v2.search_dto import SearchDTOV2
from app.utils.mmr_reranker import mmr_rerank
from app.core.database import get_db
from app.models.ptfo_tag_merged import PtfoTagMerged


class SearchServiceV2:
    """
    광고 검색 서비스 (V2).

    각 factor 별 임베딩 및 가중치를 사용하여 최종 유사도를 계산하고,
    MMR 옵션에 따라 다양한 결과를 제공한다.
    - full, desc, what, how, style: SBERT 로 유사도 계산
    - what: fastText 로 유사도 계산
    """

    def __init__(self):
        """
        초기화: SBERT와 fastText 모델 및 환경변수 로드.
        """
        self.embedding_model = SentenceTransformer(ModelConfig.EMBEDDING_MODEL)
        self.fasttext_model = fasttext.load_model(ModelConfig.WORD_EMBEDDING_MODEL_PATH)
        self.artifacts_dir = f"./artifacts/v2/{ModelConfig.EMBEDDING_MODEL}"
        self.factor_weights = (
            SearchConfig.FULL_WEIGHT,
            SearchConfig.DESC_WEIGHT,
            SearchConfig.WHAT_WEIGHT,
            SearchConfig.HOW_WEIGHT,
            SearchConfig.STYLE_WEIGHT,
        )
        self.portfolio_tag_mapping = self._load_portfolio_tag_mapping()

    @staticmethod
    def _load_portfolio_tag_mapping() -> dict:
        """
        DB에서 PTFO_SEQNO별 태그 목록을 불러온다.
        """
        db = next(get_db())
        rows = db.query(PtfoTagMerged).all()
        tag_mapping = {}
        for row in rows:
            tag_mapping.setdefault(row.PTFO_SEQNO, []).append(row.TAG_NM)
        return tag_mapping

    def search(self, request: SearchDTOV2.SearchRequest) -> List[SearchDTOV2.SearchResponse]:
        """
        사용자의 검색 요청을 처리하고, 결과를 반환한다.

        Args:
            request: SearchDTOV2.SearchRequest (검색 요청)

        Returns:
            List[SearchDTOV2.SearchResponse]: 가중치 기반 정렬된 결과 목록
        """
        factor_names = ["full", "desc", "what", "how", "style"]
        factor_scores = []
        factor_records = None

        # 각 factor별 유사도 계산
        for idx, factor_name in enumerate(factor_names):
            factor_embeddings, factor_records = self._load_factor_artifacts(factor_name)

            if factor_name == "what":
                similarities = self._compute_word_similarities_with_fasttext(
                    getattr(request, factor_name), factor_records, factor_name
                )
            else:
                query_embedding = self._get_sbert_embedding(getattr(request, factor_name))
                similarities = self._compute_similarities(query_embedding, factor_embeddings)

            factor_scores.append(similarities)

        # 가중치 기반 최종 유사도 결합
        final_scores = sum(
            (w * s for w, s in zip(self.factor_weights, factor_scores)),
            start=np.zeros_like(factor_scores[0])
        )

        # 최종 결과 생성
        results = []
        for idx, record in enumerate(factor_records):
            ptfo_seqno = record["PTFO_SEQNO"]
            tags = self.portfolio_tag_mapping.get(ptfo_seqno, [])
            results.append(
                SearchDTOV2.SearchResponse(
                    final_score=float(final_scores[idx]),
                    full_score=float(factor_scores[0][idx]),
                    desc_score=float(factor_scores[1][idx]),
                    what_score=float(factor_scores[2][idx]),
                    how_score=float(factor_scores[3][idx]),
                    style_score=float(factor_scores[4][idx]),
                    desc=record["desc"],
                    what=record["what"],
                    how=record["how"],
                    style=record["style"],
                    ptfo_seqno=ptfo_seqno,
                    ptfo_nm=record["PTFO_NM"],
                    ptfo_desc=record["PTFO_DESC"],
                    tags=tags
                )
            )

        # MMR 기반 다양성 처리
        if request.diversity:
            mmr_embeddings = self._get_all_factor_embeddings(factor_names)
            selected_indices = mmr_rerank(
                embeddings=mmr_embeddings,
                scores=final_scores,
                k=20,
                lambda_param=0.7
            )
            results_sorted = [results[i] for i in selected_indices]
        else:
            results_sorted = sorted(results, key=lambda x: x.final_score, reverse=True)

        return results_sorted

    def _load_factor_artifacts(self, factor_name: str):
        """
        factor별로 저장된 임베딩(pkl) 로드.

        Args:
            factor_name: factor 이름

        Returns:
            embeddings: np.ndarray
            records: List[dict]
        """
        pkl_path = os.path.join(self.artifacts_dir, f"{factor_name}_embeddings.pkl")
        with open(pkl_path, "rb") as f:
            artifact = pickle.load(f)
        return artifact["embeddings"], artifact["data"]

    def _get_sbert_embedding(self, text: str) -> np.ndarray:
        """
        SBERT 임베딩 계산 후 정규화.

        Args:
            text: 입력 텍스트

        Returns:
            정규화된 벡터 (np.ndarray)
        """
        emb = self.embedding_model.encode([text], convert_to_numpy=True)
        return emb / np.linalg.norm(emb, axis=1, keepdims=True)

    @staticmethod
    def _compute_similarities(query_emb: np.ndarray, factor_embeddings: np.ndarray) -> np.ndarray:
        """
        코사인 유사도 (FAISS) 계산.

        Args:
            query_emb: 쿼리 임베딩
            factor_embeddings: 데이터셋 임베딩

        Returns:
            유사도 배열 (np.ndarray)
        """
        norm_factor_embeddings = factor_embeddings / np.linalg.norm(factor_embeddings, axis=1, keepdims=True)
        index = faiss.IndexFlatIP(norm_factor_embeddings.shape[1])
        index.add(norm_factor_embeddings)
        D, _ = index.search(query_emb, len(norm_factor_embeddings))
        return D.flatten()

    def _compute_word_similarities_with_fasttext(self, query_text: str, factor_records: List[dict],
                                                  factor_name: str) -> np.ndarray:
        """
        fastText 기반으로 단어 평균 벡터의 유사도를 계산.

        Args:
            query_text: 쿼리 문자열
            factor_records: 검색 대상 레코드
            factor_name: 비교할 factor 이름

        Returns:
            유사도 배열 (np.ndarray)
        """
        similarities = []
        query_words = query_text.split()
        if not query_words:
            return np.zeros(len(factor_records))

        # 쿼리 평균 벡터
        query_vecs = [self.fasttext_model.get_word_vector(w) for w in query_words]
        query_vec = np.mean(query_vecs, axis=0)

        for record in factor_records:
            target_text = record.get(factor_name, "")
            target_words = target_text.split()
            if not target_words:
                similarities.append(0.0)
                continue

            target_vecs = [self.fasttext_model.get_word_vector(w) for w in target_words]
            target_vec = np.mean(target_vecs, axis=0)

            sim = cosine_similarity([query_vec], [target_vec])[0][0]
            similarities.append(sim)
        return np.array(similarities, dtype=np.float32)

    def _get_all_factor_embeddings(self, factor_names: List[str]) -> np.ndarray:
        """
        factor별로 SBERT 임베딩만 모아서 평균 결합.

        - "what" factor (fastText) 제외
            - 차원이 다르기 때문
        - (N, d) 형태로 반환.
        """
        sbert_factors = ["full", "desc", "how", "style"]
        embeddings_list = []

        for factor_name in sbert_factors:
            embeddings, _ = self._load_factor_artifacts(factor_name)
            embeddings_list.append(embeddings)

        # (4, N, d) → (N, d)
        avg_embeddings = np.mean(embeddings_list, axis=0)

        # 정규화
        norms = np.linalg.norm(avg_embeddings, axis=1, keepdims=True)
        avg_embeddings = avg_embeddings / (norms + 1e-8)

        return avg_embeddings