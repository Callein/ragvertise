import numpy as np
from typing import List

def mmr_rerank(
    embeddings: np.ndarray,
    scores: np.ndarray,
    k: int = 10,
    lambda_param: float = 0.5,
) -> List[int]:
    """
    MMR(Maximal Marginal Relevance) 기반으로 다양성을 고려하여 결과 인덱스를 정렬함.

    Parameters:
        embeddings (np.ndarray): 각 결과에 해당하는 임베딩 (N x d)
        scores (np.ndarray): 각 결과의 relevance 점수 (N,)
        k (int): 최종 선택할 개수
        lambda_param (float): 유사도 vs 다양성 가중치 (0 ~ 1). 높을수록 relevance 우선

    Returns:
        List[int]: MMR 기반으로 선택된 결과 인덱스 리스트
    """
    selected = []
    candidate_indices = list(range(len(scores)))

    while len(selected) < min(k, len(scores)):
        if not selected:
            # relevance 기준으로 가장 높은 점수 선택
            selected_idx = int(np.argmax(scores))
            selected.append(selected_idx)
            candidate_indices.remove(selected_idx)
            continue

        max_mmr = -np.inf
        mmr_idx = -1

        for candidate in candidate_indices:
            relevance = scores[candidate]

            # 현재 선택된 것들과의 최대 유사도
            diversity = max([
                np.dot(embeddings[candidate], embeddings[sel])
                for sel in selected
            ]) if selected else 0.0

            mmr_score = lambda_param * relevance - (1 - lambda_param) * diversity

            if mmr_score > max_mmr:
                max_mmr = mmr_score
                mmr_idx = candidate

        selected.append(mmr_idx)
        candidate_indices.remove(mmr_idx)

    return selected