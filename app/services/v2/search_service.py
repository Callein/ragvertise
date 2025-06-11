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
    def __init__(self):
        # 문장 임베딩용 SBERT
        self.embedding_model = SentenceTransformer(ModelConfig.EMBEDDING_MODEL)

        # FastText 로드
        self.fasttext_model = fasttext.load_model(ModelConfig.WORD_EMBEDDING_MODEL_PATH)

        # SBERT artifacts 경로
        self.artifacts_dir = f"./artifacts/v2/{ModelConfig.EMBEDDING_MODEL}"

        # factor별 가중치
        self.factor_weights = (
            SearchConfig.FULL_WEIGHT,
            SearchConfig.DESC_WEIGHT,
            SearchConfig.WHAT_WEIGHT,
            SearchConfig.HOW_WEIGHT,
            SearchConfig.STYLE_WEIGHT,
        )
        self.portfolio_tag_mapping = self._load_portfolio_tag_mapping()

    @staticmethod
    def _load_portfolio_tag_mapping():
        db = next(get_db())
        rows = db.query(PtfoTagMerged).all()
        tag_mapping = {}
        for row in rows:
            tag_mapping.setdefault(row.PTFO_SEQNO, []).append(row.TAG_NM)
        return tag_mapping

    def search(self, request: SearchDTOV2.SearchRequest) -> List[SearchDTOV2.SearchResponse]:
        factor_names = ["full", "desc", "what", "how", "style"]
        factor_scores = []
        factor_records = None

        # Factor별 검색
        for idx, factor_name in enumerate(factor_names):
            factor_embeddings, factor_records = self._load_factor_artifacts(factor_name)

            if factor_name == "what":
                # what factor는 fastText 방식으로 유사도 계산
                similarities = self._compute_word_similarities_with_fasttext(
                    getattr(request, factor_name), factor_records, factor_name
                )
            else:
                # SBERT 방식
                query_embedding = self._get_sbert_embedding(getattr(request, factor_name))
                similarities = self._compute_similarities(query_embedding, factor_embeddings)

            factor_scores.append(similarities)

        # Factor별 가중치 결합
        final_scores = sum(
            (w * s for w, s in zip(self.factor_weights, factor_scores)),
            start=np.zeros_like(factor_scores[0])
        )

        # 결과 DTO 생성
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

        # MMR 옵션 처리
        if request.diversity:
            mmr_embeddings = self._get_sbert_embedding(getattr(request, "full"))
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
        pkl_path = os.path.join(self.artifacts_dir, f"{factor_name}_embeddings.pkl")
        with open(pkl_path, "rb") as f:
            artifact = pickle.load(f)
        return artifact["embeddings"], artifact["data"]

    def _get_sbert_embedding(self, text: str) -> np.ndarray:
        emb = self.embedding_model.encode([text], convert_to_numpy=True)
        return emb / np.linalg.norm(emb, axis=1, keepdims=True)

    @staticmethod
    def _compute_similarities(query_emb: np.ndarray, factor_embeddings: np.ndarray) -> np.ndarray:
        norm_factor_embeddings = factor_embeddings / np.linalg.norm(factor_embeddings, axis=1, keepdims=True)
        index = faiss.IndexFlatIP(norm_factor_embeddings.shape[1])
        index.add(norm_factor_embeddings)
        D, _ = index.search(query_emb, len(norm_factor_embeddings))
        return D.flatten()

    def _compute_word_similarities_with_fasttext(self, query_text: str, factor_records: List[dict], factor_name: str) -> np.ndarray:
        similarities = []
        query_words = query_text.split()
        if not query_words:
            return np.zeros(len(factor_records))

        # 쿼리의 평균 벡터
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