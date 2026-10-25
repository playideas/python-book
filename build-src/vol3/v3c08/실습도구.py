"""8.8절 실습: 기록을 받아 EKF를 돌리고 오차를 재는 도구."""
import numpy as np

from 바퀴로봇 import 각도_감싸기, ekf_갱신, ekf_예측, 표지_R
from 바퀴장면 import 표지들


def ekf_돌리기(기록: dict, 쓸_표지: tuple[int, ...] = (0, 1, 2, 3), Q_배율: float = 1.0,
            R_배율: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """오도메트리로 예측하고 보이는 표지마다 갱신한다. 추정 경로와 걸음마다의 공분산을 돌려준다."""
    x, P = np.zeros(3), np.diag([0.01**2, 0.01**2, np.deg2rad(1.0) ** 2])
    추정, 공분산 = [], []
    for (이동, 회전), 본_표지 in zip(기록["오도"], 기록["표지"]):
        x, P = ekf_예측(x, P, 이동, 회전, Q_배율)
        for i, z in 본_표지:
            if i in 쓸_표지:
                x, P, _, _ = ekf_갱신(x, P, z, 표지들[i], R_배율 * 표지_R)
        추정.append(x)
        공분산.append(P)
    return np.array(추정), np.array(공분산)


def 오차(추정: np.ndarray, 참: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """걸음마다의 위치 오차(m)와 방향 오차(rad)."""
    return np.linalg.norm(추정[:, :2] - 참[:, :2], axis=1), 각도_감싸기(추정[:, 2] - 참[:, 2])
