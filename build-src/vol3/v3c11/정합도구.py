"""11장: 점-점 ICP로 두 스캔을 맞춘다."""
import numpy as np
from scipy.spatial import KDTree

from 포즈도구 import 점_옮기기


def 최적_변환(원본: np.ndarray, 기준: np.ndarray) -> np.ndarray:
    """짝지은 두 점구름(N×2)에서 원본을 기준에 가장 잘 겹치는 회전과 이동(3×3)을 SVD로 구한다."""
    원본_중심, 기준_중심 = 원본.mean(axis=0), 기준.mean(axis=0)
    H = (원본 - 원본_중심).T @ (기준 - 기준_중심)          # 2×2 공분산
    U, _, Vt = np.linalg.svd(H)
    D = np.diag([1.0, np.sign(np.linalg.det(Vt.T @ U.T))])  # 거울에 비친 답(행렬식 -1)을 막는다
    R = Vt.T @ D @ U.T
    T = np.eye(3)
    T[:2, :2] = R
    T[:2, 2] = 기준_중심 - R @ 원본_중심
    return T


def icp(원본: np.ndarray, 기준: np.ndarray, 초기_T: np.ndarray | None = None,
        반복: int = 60, 짝_한계: float = 0.5, 멈춤: float = 1e-6):
    """원본 점들을 기준 점들에 맞추는 변환 T(3×3)와 반복마다의 평균 짝 거리를 돌려준다.

    원본이 '지금' 스캔, 기준이 '이전' 스캔이면 T는 T_이전_지금이다.
    """
    트리 = KDTree(기준)
    T = np.eye(3) if 초기_T is None else 초기_T.copy()
    기록 = []
    for _ in range(반복):
        옮긴 = 점_옮기기(T, 원본)
        거리, 번호 = 트리.query(옮긴)                     # 1) 가장 가까운 점을 짝으로
        좋은 = 거리 < 짝_한계                             # 2) 너무 먼 짝은 버린다
        기록.append(float(np.minimum(거리, 짝_한계).mean()))   # 먼 짝은 한계값으로 세어 평균
        변화 = 최적_변환(옮긴[좋은], 기준[번호[좋은]])    # 3) 짝을 가장 잘 겹치는 변환
        T = 변화 @ T                                      # 4) 쌓고 다시 1)로
        if np.abs(변화 - np.eye(3)).max() < 멈춤:
            break
    return T, 기록
