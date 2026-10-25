"""15장: 관절 목표 경로 만들기. 작업 공간 직선과 관절 공간 직선."""
import numpy as np
from scipy.spatial.transform import Rotation, Slerp

from 잡기도구 import TCP_포즈, 역기구학
from 팔도구 import 변환

제어_주기 = 0.01          # 100Hz로 관절 목표를 보낸다


def 부드럽게(s: float) -> float:
    """0→1을 출발과 도착에서 속도가 0이 되게 잇는 곡선(3s² - 2s³)."""
    return 3 * s**2 - 2 * s**3


def 직선_경로(q_시작, T_끝: np.ndarray, 시간: float) -> list[np.ndarray]:
    """TCP가 곧은 선을 따라가는 관절 목표 목록. 위치는 선형, 자세는 slerp(2장)."""
    T_시작 = TCP_포즈(q_시작)
    자세 = Slerp([0, 1], Rotation.from_matrix([T_시작[:3, :3], T_끝[:3, :3]]))
    q, 경로 = np.array(q_시작, dtype=float), []
    for k in range(1, int(round(시간 / 제어_주기)) + 1):
        s = 부드럽게(k * 제어_주기 / 시간)
        T = 변환(자세(s).as_matrix(), (1 - s) * T_시작[:3, 3] + s * T_끝[:3, 3])
        q = 역기구학(T, q, 반복=10)              # 바로 앞 점의 답에서 출발(3장 3.10절)
        경로.append(q)
    return 경로


def 관절_경로(q_시작, q_끝, 시간: float) -> list[np.ndarray]:
    """관절 각도를 곧게 잇는 목표 목록. TCP가 지나는 길은 정하지 않는다."""
    n = int(round(시간 / 제어_주기))
    return [q_시작 + 부드럽게(k / n) * (np.asarray(q_끝) - q_시작) for k in range(1, n + 1)]
