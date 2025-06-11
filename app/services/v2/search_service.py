from typing import List
import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from app.core.config import SearchConfig, ModelConfig
from app.schemas.v2.search_dto import SearchDTOV2
from app.utils.mmr_reranker import mmr_rerank

class SearchServiceV2:
    def __init__(self):
        self.embedding_model = SentenceTransformer(ModelConfig.EMBEDDING_MODEL)
        self.artifacts_dir = f"./artifacts/v2/{ModelConfig.EMBEDDING_MODEL}"
        self.factor_weights = (
            SearchConfig.DESC_WEIGHT,
            SearchConfig.WHAT_WEIGHT,
            SearchConfig.HOW_WEIGHT,
            SearchConfig.STYLE_WEIGHT,
        )

    def search(self, request: SearchDTOV2.SearchRequest) -> List[SearchDTOV2.SearchResponse]:
        factor_scores = []
        factor_names = ["desc", "what", "how", "style"]
        factor_records = None  # 나중에 최종 사용

        # Factor 별 검색
        for factor_name in factor_names:
            factor_embeddings, factor_records = self._load_factor_artifacts(factor_name)
            query_embedding = self._get_embedding(getattr(request, factor_name))
            similarities = self._compute_similarities(query_embedding, factor_embeddings)
            factor_scores.append(similarities)

        # Factor 별 가중치 결합
        final_scores = sum(
            (w * s for w, s in zip(self.factor_weights, factor_scores)),
            start=np.zeros_like(factor_scores[0])
        )

        # 결과 DTO 생성
        results = []
        for idx, record in enumerate(factor_records):
            results.append(
                SearchDTOV2.SearchResponse(
                    final_score=float(final_scores[idx]),
                    text_score=float(factor_scores[0][idx]),  # desc
                    what_score=float(factor_scores[1][idx]),
                    how_score=float(factor_scores[2][idx]),
                    style_score=float(factor_scores[3][idx]),
                    ptfo_seqno=record["PTFO_SEQNO"],
                    ptfo_nm=record["PTFO_NM"],
                    ptfo_desc=record["PTFO_DESC"],
                    tag_names=record.get("tag_names", [])
                )
            )

        # MMR 옵션 처리
        if request.diversity:
            selected_indices = mmr_rerank(
                embeddings=np.array([r["embedding"] for r in factor_records]),
                scores=final_scores,
                k=20,
                lambda_param=0.7
            )
            results_sorted = [results[i] for i in selected_indices]
        else:
            results_sorted = sorted(results, key=lambda x: x.final_score, reverse=True)

        return results_sorted

    def _load_factor_artifacts(self, factor_name: str):
        pkl_path = os.path.join(self.artifacts_dir, f"{factor_name}_embeddings.pkl")
        with open(pkl_path, "rb") as f:
            artifact = pickle.load(f)
        return artifact["embeddings"], artifact["data"]

    def _get_embedding(self, text: str) -> np.ndarray:
        emb = self.embedding_model.encode([text], convert_to_numpy=True)
        return emb / np.linalg.norm(emb, axis=1, keepdims=True)

    @staticmethod
    def _compute_similarities(query_emb: np.ndarray, factor_embeddings: np.ndarray) -> np.ndarray:
        # 정규화 된 내적 기반 유사도
        norm_factor_embeddings = factor_embeddings / np.linalg.norm(factor_embeddings, axis=1, keepdims=True)
        index = faiss.IndexFlatIP(norm_factor_embeddings.shape[1])
        index.add(norm_factor_embeddings)
        D, _ = index.search(query_emb, len(norm_factor_embeddings))
        return D.flatten()