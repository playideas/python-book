"""8장: 바퀴 둘 달린 로봇의 EKF 부품. 상태는 지도 기준 [x, y, θ](m, m, rad)."""
import numpy as np


def 각도_감싸기(각: float | np.ndarray) -> float | np.ndarray:
    """각도를 -π 이상 π 미만으로 접는다."""
    return (각 + np.pi) % (2 * np.pi) - np.pi


def 움직이기(상태: np.ndarray, 이동: float, 회전: float) -> np.ndarray:
    """움직임 모델 f: 오도메트리가 알려 준 이동 거리(m)와 회전(rad)만큼 옮긴다."""
    x, y, θ = 상태
    가운데 = θ + 회전 / 2                       # 도는 도중의 방향으로 이동했다고 본다
    return np.array([x + 이동 * np.cos(가운데), y + 이동 * np.sin(가운데), 각도_감싸기(θ + 회전)])


def 움직임_야코비안(상태: np.ndarray, 이동: float, 회전: float) -> tuple[np.ndarray, np.ndarray]:
    """F = ∂f/∂상태, V = ∂f/∂[이동, 회전]."""
    가운데 = 상태[2] + 회전 / 2
    c, s = np.cos(가운데), np.sin(가운데)
    F = np.array([[1, 0, -이동 * s],
                  [0, 1, 이동 * c],
                  [0, 0, 1]])
    V = np.array([[c, -이동 * s / 2],
                  [s, 이동 * c / 2],
                  [0, 1]])
    return F, V


def 움직임_잡음(상태: np.ndarray, 이동: float, 회전: float) -> np.ndarray:
    """오도메트리 잡음(이동의 5%, 회전의 5% + 1m당 0.05rad)을 상태 공간의 Q로 옮긴다."""
    M = np.diag([(0.05 * abs(이동) + 1e-4) ** 2, (0.05 * abs(회전) + 0.05 * abs(이동)) ** 2])
    _, V = 움직임_야코비안(상태, 이동, 회전)
    return V @ M @ V.T


def 표지_보기(상태: np.ndarray, 표지: np.ndarray) -> np.ndarray:
    """측정 모델 h: 로봇에서 본 표지까지의 [거리(m), 방향(rad)]."""
    dx, dy = 표지[0] - 상태[0], 표지[1] - 상태[1]
    return np.array([np.hypot(dx, dy), 각도_감싸기(np.arctan2(dy, dx) - 상태[2])])


def 표지_야코비안(상태: np.ndarray, 표지: np.ndarray) -> np.ndarray:
    """H = ∂h/∂상태."""
    dx, dy = 표지[0] - 상태[0], 표지[1] - 상태[1]
    q = dx**2 + dy**2
    r = np.sqrt(q)
    return np.array([[-dx / r, -dy / r, 0],
                     [dy / q, -dx / q, -1]])


def ekf_예측(x: np.ndarray, P: np.ndarray, 이동: float, 회전: float,
           Q_배율: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    F, _ = 움직임_야코비안(x, 이동, 회전)
    return 움직이기(x, 이동, 회전), F @ P @ F.T + Q_배율 * 움직임_잡음(x, 이동, 회전)


def ekf_갱신(x: np.ndarray, P: np.ndarray, z: np.ndarray, 표지: np.ndarray,
           R: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    H = 표지_야코비안(x, 표지)
    혁신 = z - 표지_보기(x, 표지)
    혁신[1] = 각도_감싸기(혁신[1])              # 방향 차이도 -π~π로 접어야 한다
    S = H @ P @ H.T + R
    K = P @ H.T @ np.linalg.inv(S)
    x = x + K @ 혁신
    x[2] = 각도_감싸기(x[2])
    P = (np.eye(3) - K @ H) @ P
    return x, P, 혁신, S


표지_R = np.diag([0.05**2, np.deg2rad(2.0) ** 2])     # 거리 잡음 0.05m, 방향 잡음 2도
