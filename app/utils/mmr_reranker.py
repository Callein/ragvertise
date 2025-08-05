import numpy as np
from typing import List


def mmr_rerank(
        embeddings: np.ndarray,
        scores: np.ndarray,
        k: int = 10,
        lambda_param: float = 0.5
) -> List[int]:
    """
    MMR 기반으로 결과의 다양성과 relevance를 균형 있게 반영해 상위 k개 인덱스를 반환.

    Parameters:
        embeddings (np.ndarray): (N, D) 형태의 임베딩 벡터들.
        scores (np.ndarray): (N,) relevance 점수.
        k (int): 선택할 개수 (최대 N).
        lambda_param (float): relevance vs. diversity 가중치 (0~1).

    Returns:
        List[int]: 선택된 결과 인덱스 리스트.
    """
    N = embeddings.shape[0]
    k = min(k, N)

    if k == 1 or N == 1:
        return [int(np.argmax(scores))]

    # 선택 결과 인덱스
    selected = []
    # 후보군 인덱스
    candidate_indices = list(range(N))

    # 1. relevance 기준 첫 번째 선택
    first_idx = int(np.argmax(scores))
    selected.append(first_idx)
    candidate_indices.remove(first_idx)

    # 2. 나머지 k-1개 선택
    while len(selected) < k and candidate_indices:
        max_score = -np.inf
        best_idx = -1

        for candidate in candidate_indices:
            # relevance
            rel = scores[candidate]
            # diversity: 기존 선택된 것들과의 최대 유사도 (코사인 유사도)
            diversity = max(
                np.dot(embeddings[candidate], embeddings[sel])
                / (np.linalg.norm(embeddings[candidate]) * np.linalg.norm(embeddings[sel]) + 1e-10)
                for sel in selected
            )
            # MMR 점수 계산
            mmr_score = lambda_param * rel - (1 - lambda_param) * diversity

            if mmr_score > max_score:
                max_score = mmr_score
                best_idx = candidate

        if best_idx == -1:
            break
        selected.append(best_idx)
        candidate_indices.remove(best_idx)

    return selected