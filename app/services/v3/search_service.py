from typing import List, Dict, Tuple
import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import fasttext

from app.core.config import ModelConfig, SearchConfig
from app.schemas.v2.search_dto import SearchDTOV2
from app.utils.mmr_reranker import mmr_rerank
from app.core.database import get_db
from app.models.ptfo_tag_merged import PtfoTagMerged

class SearchServiceV3:
    """
    - 부팅 시 1회 로드(싱글톤): fused_index / factor embeddings / tag mapping
    - 요청 시: fused 검색 1회 → 후보에 한해 factor별 점수/최종점수 계산
    - DB 세션은 __init__에서만 잠깐 쓰고 닫음(요청마다 열지 않음)
    """

    # 후보 폭(튜닝)
    ALPHA = 4
    MIN_CANDS = 10
    MAX_CANDS_CAP = 500
    FACTOR_ORDER = ["full", "desc", "what", "how", "style"]

    def __init__(self):
        # 모델(읽기 전용)
        self.embedding_model = SentenceTransformer(ModelConfig.EMBEDDING_MODEL)
        self.fasttext_model = fasttext.load_model(ModelConfig.WORD_EMBEDDING_MODEL_PATH)
        self.artifacts_dir = f"./artifacts/v3/{ModelConfig.EMBEDDING_MODEL}"

        # factor별 원본 임베딩 + 메타 (후보 점수 계산용)
        self.embeddings: Dict[str, np.ndarray] = {}
        self.records = None

        for f in self.FACTOR_ORDER:
            with open(os.path.join(self.artifacts_dir, f"{f}_embeddings.pkl"), "rb") as fp:
                meta = pickle.load(fp)
            self.embeddings[f] = meta["embeddings"]
            if self.records is None:
                self.records = meta["data"]

        # fused 인덱스/메타 (검색용)
        self.fused_index = faiss.read_index(os.path.join(self.artifacts_dir, "fused_index.faiss"))
        with open(os.path.join(self.artifacts_dir, "fused_embeddings.pkl"), "rb") as fp:
            fused_meta = pickle.load(fp)
        self.weights = fused_meta["weights"]
        self.sqrt_w = {k: np.sqrt(float(v)).astype(np.float32) for k, v in self.weights.items()}

        # 태그 매핑(읽기 전용 dict) — 여기서만 DB 세션을 열고 닫음
        self.portfolio_tag_mapping = self._load_tag_mapping_once()

    @staticmethod
    def _load_tag_mapping_once() -> Dict[int, List[str]]:
        db = next(get_db())
        try:
            rows = db.query(PtfoTagMerged).all()
            tag_mapping: Dict[int, List[str]] = {}
            for r in rows:
                tag_mapping.setdefault(r.PTFO_SEQNO, []).append(r.TAG_NM)
            return tag_mapping
        finally:
            # get_db 제너레이터가 알아서 정리하지만, 혹시 커스텀이라면 명시 종료 고려
            pass

    # ----- 임베딩 유틸 -----
    @staticmethod
    def _l2norm(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
        return x / (np.linalg.norm(x, axis=1, keepdims=True) + eps)

    def _embed_sbert(self, text: str) -> np.ndarray:
        v = self.embedding_model.encode([text or ""], convert_to_numpy=True).astype(np.float32)
        return self._l2norm(v)

    def _embed_fasttext(self, text: str) -> np.ndarray:
        words = (text or "").split()
        if not words:
            v = np.zeros((1, self.fasttext_model.get_dimension()), dtype=np.float32)
        else:
            mat = np.stack([self.fasttext_model.get_word_vector(w) for w in words], axis=0).astype(np.float32)
            v = mat.mean(axis=0, keepdims=True)
        return self._l2norm(v)

    def _embed_query_fused(self, req: SearchDTOV2.SearchRequest):
        q = {
            "full":  self._embed_sbert(req.full),
            "desc":  self._embed_sbert(req.desc),
            "what":  self._embed_fasttext(req.what),
            "how":   self._embed_sbert(req.how),
            "style": self._embed_sbert(req.style),
        }
        scaled = [q[f] * self.sqrt_w[f] for f in self.FACTOR_ORDER]
        q_fused = np.concatenate(scaled, axis=1).astype(np.float32)
        return q_fused, q

    # ----- 퍼블릭 검색 -----
    def search(self, request: SearchDTOV2.SearchRequest):
        k = int(request.limit or 5)
        N = int(self.fused_index.ntotal)
        if N <= 0:
            return []

        # diversity 켜졌을 때만 후보폭 사용, 아니면 K만 검색해서 비용 최소화
        if request.diversity:
            M = min(N, max(k * self.ALPHA, self.MIN_CANDS))
            M = min(M, self.MAX_CANDS_CAP)
        else:
            M = min(k, N)

        q_fused, q_fac = self._embed_query_fused(request)

        D, I = self.fused_index.search(q_fused, M)
        I0 = I[0].astype(int)
        D0 = D[0].astype(np.float32)
        keep = (I0 != -1) & np.isfinite(D0)
        cand_ids = I0[keep].tolist()
        if not cand_ids:
            return []

        # 후보(보통 K 또는 M)에 대해서만 factor 점수 계산
        def dot_scores(qv: np.ndarray, mat: np.ndarray) -> np.ndarray:
            return (qv @ mat.T).astype(np.float32)[0]

        full_s  = dot_scores(q_fac["full"],  self.embeddings["full"][cand_ids])
        desc_s  = dot_scores(q_fac["desc"],  self.embeddings["desc"][cand_ids])
        what_s  = dot_scores(q_fac["what"],  self.embeddings["what"][cand_ids])
        how_s   = dot_scores(q_fac["how"],   self.embeddings["how"][cand_ids])
        style_s = dot_scores(q_fac["style"], self.embeddings["style"][cand_ids])

        Wf = float(self.weights["full"]);  Wd = float(self.weights["desc"])
        Ww = float(self.weights["what"]);  Wh = float(self.weights["how"]);  Ws = float(self.weights["style"])
        final_scores = (Wf*full_s + Wd*desc_s + Ww*what_s + Wh*how_s + Ws*style_s).astype(np.float32)
        final_scores = np.where(np.isfinite(final_scores), final_scores, 0.0)

        # 순위 선택
        if request.diversity:
            mmr_emb = self._avg_sbert_emb_subset(cand_ids)
            sel = mmr_rerank(mmr_emb, final_scores, k=min(k, len(cand_ids)), lambda_param=0.7)
            order_idx = sel
        else:
            order_idx = np.argsort(-final_scores)[:k]

        ordered_ids = [cand_ids[i] for i in order_idx]

        # DTO 변환
        from app.schemas.v2.search_dto import SearchDTOV2 as S  # 순환 임포트 회피용
        results: List[S.SearchResponse] = []
        for j, gid in zip(order_idx, ordered_ids):
            rec = self.records[gid]
            ptfo_seqno = rec["PTFO_SEQNO"]
            tags = self.portfolio_tag_mapping.get(ptfo_seqno, [])
            results.append(
                S.SearchResponse(
                    final_score=float(final_scores[j]),
                    full_score=float(full_s[j]),
                    desc_score=float(desc_s[j]),
                    what_score=float(what_s[j]),
                    how_score=float(how_s[j]),
                    style_score=float(style_s[j]),
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

    def _avg_sbert_emb_subset(self, cand_ids: List[int]) -> np.ndarray:
        mats = [
            self.embeddings["full"][cand_ids],
            self.embeddings["desc"][cand_ids],
            self.embeddings["how"][cand_ids],
            self.embeddings["style"][cand_ids],
        ]
        avg = np.mean(mats, axis=0)
        avg /= (np.linalg.norm(avg, axis=1, keepdims=True) + 1e-8)
        return avg

    # (선택) 랭크 서비스에서 코퍼스 상한용
    def corpus_size(self) -> int:
        return int(self.fused_index.ntotal)


# ----- 전역 싱글톤 인스턴스 (앱 부팅 시 1회만 생성) -----
search_service_singleton = SearchServiceV3()