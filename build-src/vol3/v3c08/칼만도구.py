"""8장: 선형 칼만 필터의 예측과 갱신. 상태 x는 1차원 배열, 나머지는 행렬."""
import numpy as np


def 예측(x: np.ndarray, P: np.ndarray, F: np.ndarray, Q: np.ndarray,
       B: np.ndarray | None = None, u: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """움직임 모델로 한 걸음 내다본다. 불확실성 P는 F로 옮겨지고 Q만큼 커진다."""
    x = F @ x if B is None else F @ x + B @ u
    P = F @ P @ F.T + Q
    return x, P


def 갱신(x: np.ndarray, P: np.ndarray, z: np.ndarray, H: np.ndarray,
       R: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """측정 z로 고친다. 고친 상태, 공분산, 혁신(잰 값 - 예상한 값), 혁신의 공분산 S를 돌려준다."""
    혁신 = z - H @ x
    S = H @ P @ H.T + R
    K = P @ H.T @ np.linalg.inv(S)          # 칼만 이득
    x = x + K @ 혁신
    P = (np.eye(len(x)) - K @ H) @ P
    return x, P, 혁신, S
