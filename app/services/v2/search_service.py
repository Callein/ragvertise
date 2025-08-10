from typing import List, Dict, Tuple
import os
import pickle
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer
import fasttext

from app.core.config import SearchConfig, ModelConfig
from app.schemas.v2.search_dto import SearchDTOV2
from app.utils.mmr_reranker import mmr_rerank
from app.core.database import get_db
from app.models.ptfo_tag_merged import PtfoTagMerged


class SearchServiceV2:
    """
    광고 검색 서비스 (V2).

    - full/desc/how/style: SBERT 임베딩 + FAISS(IndexFlatIP)에서 top-M 후보 검색
    - what: fastText 평균 임베딩 + 동일하게 top-M 후보 검색
    - 후보만 대상으로 가중합/다양성(MMR) 적용 → 최종 top-K 반환
    - limit > N 시 안전 가드(클램핑) 및 FAISS -1/-inf 결과 필터
    """

    CANDIDATE_MULTIPLIER = 8   # M = K * multiplier
    MIN_CANDIDATES = 50        # 후보 최소 개수

    def __init__(self):
        self.embedding_model = SentenceTransformer(ModelConfig.EMBEDDING_MODEL)
        self.fasttext_model = fasttext.load_model(ModelConfig.WORD_EMBEDDING_MODEL_PATH)
        self.artifacts_dir = f"./artifacts/v2/{ModelConfig.EMBEDDING_MODEL}"

        self.factor_names = ["full", "desc", "what", "how", "style"]
        self.factor_weights = (
            SearchConfig.FULL_WEIGHT,
            SearchConfig.DESC_WEIGHT,
            SearchConfig.WHAT_WEIGHT,
            SearchConfig.HOW_WEIGHT,
            SearchConfig.STYLE_WEIGHT,
        )

        self.indices: Dict[str, faiss.Index] = {}
        self.embeddings: Dict[str, np.ndarray] = {}
        self.records = None

        for f in self.factor_names:
            self.indices[f] = faiss.read_index(os.path.join(self.artifacts_dir, f"{f}_index.faiss"))
            with open(os.path.join(self.artifacts_dir, f"{f}_embeddings.pkl"), "rb") as fp:
                meta = pickle.load(fp)
            self.embeddings[f] = meta["embeddings"]  # shape: (N, d_f)
            if self.records is None:
                self.records = meta["data"]

        self.portfolio_tag_mapping = self._load_portfolio_tag_mapping()

    @staticmethod
    def _load_portfolio_tag_mapping() -> dict:
        """
        DB에서 PTFO_SEQNO별 태그 목록을 불러옴
        """
        db = next(get_db())
        rows = db.query(PtfoTagMerged).all()
        tag_mapping = {}
        for row in rows:
            tag_mapping.setdefault(row.PTFO_SEQNO, []).append(row.TAG_NM)
        return tag_mapping

    # ---------- 쿼리 임베딩 ----------

    def _embed_query_sbert(self, text: str) -> np.ndarray:
        emb = self.embedding_model.encode([text or ""], convert_to_numpy=True).astype(np.float32)
        emb /= (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-8)
        return emb  # (1, d)

    def _embed_query_fasttext(self, text: str) -> np.ndarray:
        words = (text or "").split()
        if not words:
            vec = np.zeros((1, self.fasttext_model.get_dimension()), dtype=np.float32)
        else:
            vec = np.mean([self.fasttext_model.get_word_vector(w) for w in words], axis=0).astype(np.float32)[None, :]
        vec /= (np.linalg.norm(vec, axis=1, keepdims=True) + 1e-8)
        return vec  # (1, d)

    # ---------- 퍼블릭 검색 ----------

    def search(self, request: SearchDTOV2.SearchRequest) -> List[SearchDTOV2.SearchResponse]:
        """
        전수조사 없이 factor별 인덱스에서 top-M 후보만 가져와 가중합/다양성 적용 후 top-K 반환.
        """
        # 0) K/M 설정 및 코퍼스 크기 N 기반 가드
        k = int(request.limit or 5)
        N = int(self.indices["full"].ntotal) if "full" in self.indices else 0
        if N <= 0:
            return []

        # 후보폭
        M = max(self.MIN_CANDIDATES, k * self.CANDIDATE_MULTIPLIER)
        # 코퍼스 상한 가드
        if k > N:
            k = N
        if M > N:
            M = N

        # 1) factor별 쿼리 임베딩
        q = {
            "full":  self._embed_query_sbert(request.full),
            "desc":  self._embed_query_sbert(request.desc),
            "what":  self._embed_query_fasttext(request.what),
            "how":   self._embed_query_sbert(request.how),
            "style": self._embed_query_sbert(request.style),
        }

        # 2) factor별 top-M 검색 (IndexFlatIP, 벡터 L2정규화 가정 → 내적 == cos)
        factor_scores: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}  # f -> (D0, I0)
        candidate_sets = []
        for f in self.factor_names:
            idx = self.indices[f]
            Nf = int(idx.ntotal)
            if Nf <= 0:
                continue

            kf = min(M, Nf)
            D, I = idx.search(q[f], kf)  # (1, kf)

            I0 = I[0].astype(int)
            D0 = D[0].astype(np.float32)

            # -1 인덱스/비유한수 제거
            keep = (I0 != -1) & np.isfinite(D0)
            I0 = I0[keep]
            D0 = D0[keep]

            factor_scores[f] = (D0, I0)
            candidate_sets.append(set(I0.tolist()))

        # 후보 합집합
        cand_ids = sorted(set().union(*candidate_sets)) if candidate_sets else []
        if not cand_ids:
            return []

        # 3) 가중합 점수 계산
        weights = dict(zip(self.factor_names, self.factor_weights))
        final_scores = np.zeros(len(cand_ids), dtype=np.float32)
        comp_scores = {f: np.zeros(len(cand_ids), dtype=np.float32) for f in self.factor_names}

        # 빠른 위치 맵
        pos_maps: Dict[str, Dict[int, int]] = {}
        for f, (Df, If) in factor_scores.items():
            pos_maps[f] = {int(gid): i for i, gid in enumerate(If.tolist())}

        for j, gid in enumerate(cand_ids):
            score_sum = 0.0
            for f in self.factor_names:
                pos = pos_maps.get(f, {}).get(int(gid))
                s = float(factor_scores[f][0][pos]) if pos is not None else 0.0
                if not np.isfinite(s):
                    s = 0.0
                comp_scores[f][j] = s
                score_sum += weights.get(f, 0.0) * s
            if not np.isfinite(score_sum):
                score_sum = 0.0
            final_scores[j] = np.float32(score_sum)

        # 4) 정렬/다양성(MMR)
        fs = np.where(np.isfinite(final_scores), final_scores, 0.0).astype(np.float32)

        if request.diversity:
            # 후보에 대해서만 평균 SBERT 임베딩 사용
            mmr_emb = self._get_avg_sbert_embeddings_subset(cand_ids)
            selected_indices = mmr_rerank(
                embeddings=mmr_emb,
                scores=fs,
                k=k,
                lambda_param=0.7,
            )
            ordered_ids = [cand_ids[i] for i in selected_indices]
        else:
            order = np.argsort(-fs)
            ordered_ids = [cand_ids[i] for i in order[:k]]

        # 5) DTO 변환
        idx_map = {gid: i for i, gid in enumerate(cand_ids)}
        results: List[SearchDTOV2.SearchResponse] = []

        for gid in ordered_ids:
            j = idx_map[gid]
            rec = self.records[gid]
            ptfo_seqno = rec["PTFO_SEQNO"]
            tags = self.portfolio_tag_mapping.get(ptfo_seqno, [])

            results.append(
                SearchDTOV2.SearchResponse(
                    final_score=float(fs[j]),
                    full_score=float(comp_scores["full"][j]),
                    desc_score=float(comp_scores["desc"][j]),
                    what_score=float(comp_scores["what"][j]),
                    how_score=float(comp_scores["how"][j]),
                    style_score=float(comp_scores["style"][j]),
                    desc=rec["desc"],
                    what=rec["what"],
                    how=rec["how"],
                    style=rec["style"],
                    ptfo_seqno=ptfo_seqno,
                    ptfo_nm=rec["PTFO_NM"],
                    ptfo_desc=rec["PTFO_DESC"],
                    tags=tags,
                )
            )

        return results

    # ---------- helpers ----------

    def _get_avg_sbert_embeddings_subset(self, cand_ids: List[int]) -> np.ndarray:
        """
        MMR용 임베딩: SBERT factors(full, desc, how, style)의 평균 임베딩을
        후보 서브셋에 대해 계산 후 L2 정규화하여 반환.
        """
        sbert_factors = ["full", "desc", "how", "style"]
        mats = [self.embeddings[f][cand_ids] for f in sbert_factors]  # 각 (len(cands), d)
        avg = np.mean(mats, axis=0)
        avg /= (np.linalg.norm(avg, axis=1, keepdims=True) + 1e-8)
        return avg
