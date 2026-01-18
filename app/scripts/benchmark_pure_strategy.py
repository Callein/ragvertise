import time
import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import fasttext

# 프로젝트 설정 (경로 및 모델명 확인)
from app.core.config import ModelConfig, SearchConfig

# ==========================================
# 1. 설정 및 리소스 로딩 (한 번만 실행)
# ==========================================
class BenchmarkResources:
    def __init__(self):
        print("⏳ [Init] 모델 및 인덱스 로딩 중... (메모리 확보 필요)")
        
        # 1. 모델 로딩 (공통)
        self.sbert = SentenceTransformer(ModelConfig.EMBEDDING_MODEL)
        self.ft = fasttext.load_model(ModelConfig.WORD_EMBEDDING_MODEL_PATH)
        
        # 2. V2 (Naive) 리소스 로딩
        self.v2_indices = {}
        self.v2_dir = f"./artifacts/v2/{ModelConfig.EMBEDDING_MODEL}"
        factors = ["full", "desc", "what", "how", "style"]
        
        for f in factors:
            idx_path = os.path.join(self.v2_dir, f"{f}_index.faiss")
            if os.path.exists(idx_path):
                self.v2_indices[f] = faiss.read_index(idx_path)
            else:
                print(f"⚠️ V2 인덱스 없음: {idx_path} (먼저 생성해주세요)")

        # 3. V3 (Fused) 리소스 로딩
        self.v3_dir = f"./artifacts/v3/{ModelConfig.EMBEDDING_MODEL}"
        self.v3_index = faiss.read_index(os.path.join(self.v3_dir, "fused_index.faiss"))
        
        with open(os.path.join(self.v3_dir, "fused_embeddings.pkl"), "rb") as f:
            meta = pickle.load(f)
            self.weights = meta["weights"]
            # numpy float32로 변환된 sqrt 가중치 미리 계산
            self.sqrt_w = {k: np.sqrt(float(v)).astype(np.float32) for k, v in self.weights.items()}

        print("✅ 로딩 완료! 벤치마크 시작...\n")

    # 헬퍼: L2 정규화
    def l2norm(self, x):
        return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-8)

    # 헬퍼: 임베딩 생성
    def get_embedding(self, text, factor):
        if factor == "what":
            words = text.split()
            if not words: return np.zeros((1, self.ft.get_dimension()), dtype=np.float32)
            mat = np.stack([self.ft.get_word_vector(w) for w in words])
            return self.l2norm(mat.mean(axis=0, keepdims=True))
        else:
            return self.l2norm(self.sbert.encode([text], convert_to_numpy=True))

# ==========================================
# 2. V2 로직 (Naive Late Fusion)
# ==========================================
def search_v2_naive(res: BenchmarkResources, query_parts):
    # 1. 5번의 임베딩 (사실 이 시간은 동일함)
    q_embs = {}
    for f, text in query_parts.items():
        q_embs[f] = res.get_embedding(text, f)
    
    # 2. [핵심 병목] 5번의 FAISS 검색 + Python 레벨 병합
    results = {}
    
    # (1) Desc 검색
    D, I = res.v2_indices["desc"].search(q_embs["desc"], 50)
    # (2) What 검색
    D, I = res.v2_indices["what"].search(q_embs["what"], 50)
    # (3) How 검색
    D, I = res.v2_indices["how"].search(q_embs["how"], 50)
    # (4) Style 검색
    D, I = res.v2_indices["style"].search(q_embs["style"], 50)
    # (5) Full 검색
    D, I = res.v2_indices["full"].search(q_embs["full"], 50)
    
    # ※ 실제로는 여기서 ID 매핑해서 점수 더하는 복잡한 로직(Late Fusion)이 들어감.
    #    단순 검색 시간만 비교해도 5배 차이가 나므로 여기까지만 측정.
    return D

# ==========================================
# 3. V3 로직 (Weighted Late Fusion)
# ==========================================
def search_v3_fused(res: BenchmarkResources, query_parts):
    # 1. 임베딩 + 가중치 적용 + Concat (한 번에 수행)
    vecs = []
    order = ["full", "desc", "what", "how", "style"]
    
    for f in order:
        raw = res.get_embedding(query_parts[f], f)
        # √가중치 곱하기 (Linearity 활용)
        vecs.append(raw * res.sqrt_w[f])
        
    fused_query = np.concatenate(vecs, axis=1).astype(np.float32)
    
    # 2. [최적화] 단 1번의 FAISS 검색
    D, I = res.v3_index.search(fused_query, 50)
    return D

# ==========================================
# 4. 실행 및 리포트
# ==========================================
def run_benchmark():
    # 리소스 초기화
    res = BenchmarkResources()
    
    # 테스트 쿼리
    query_parts = {
        "full": "세련되고 감각적인 뷰티 광고 립스틱",
        "desc": "세련되고 감각적인 뷰티 광고",
        "what": "립스틱",
        "how": "빠른 편집",
        "style": "비비드한"
    }
    
    iterations = 100
    
    # --- V2 측정 ---
    print(f"🔹 [V2 Naive] 5번 검색 x {iterations}회")
    t_start = time.perf_counter()
    for _ in range(iterations):
        search_v2_naive(res, query_parts)
    t_v2 = (time.perf_counter() - t_start) / iterations * 1000  # ms
    
    # --- V3 측정 ---
    print(f"🔹 [V3 Fused] 1번 검색 x {iterations}회")
    t_start = time.perf_counter()
    for _ in range(iterations):
        search_v3_fused(res, query_parts)
    t_v3 = (time.perf_counter() - t_start) / iterations * 1000 # ms
    
    # --- 결과 출력 ---
    print("\n" + "="*50)
    print("📊 [Pure Algorithm Benchmark Result]")
    print("="*50)
    print(f"1. V2 (Naive, 5 Searches): {t_v2:.4f} ms")
    print(f"2. V3 (Fused, 1 Search) : {t_v3:.4f} ms")
    print("-" * 50)
    if t_v3 < t_v2:
        print(f"🚀 Speedup: {t_v2 / t_v3:.2f}x faster")
        print(f"📉 Latency Reduction: -{t_v2 - t_v3:.4f} ms")
    else:
        print("⚠️ 차이가 미미하거나 V3가 더 느림 (데이터셋 크기가 작을 수 있음)")
    print("="*50)

if __name__ == "__main__":
    run_benchmark()