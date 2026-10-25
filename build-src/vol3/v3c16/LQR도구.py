"""16장: 이산 시간 LQR 이득."""
import numpy as np
from scipy.linalg import solve_discrete_are


def LQR(A: np.ndarray, B: np.ndarray, Q: np.ndarray, R: float) -> tuple[np.ndarray, np.ndarray]:
    """끝없이 긴 구간의 최적 이득 K(u = -K x)와 비용 행렬 P."""
    P = solve_discrete_are(A, B, Q, R)
    K = np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A)
    return K, P
