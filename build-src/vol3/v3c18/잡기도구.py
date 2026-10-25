"""15장: 집는 자세와 역기구학. 3장의 팔도구·야코비안도구를 집게의 TCP에 맞춰 쓴다."""
import numpy as np
from scipy.spatial.transform import Rotation

from 야코비안도구 import 야코비안
from 팔도구 import 변환, 역변환, 순기구학
from 팔집게장면 import T_세계_받침, 손끝_집게
from 회전도구 import Rx, Rz


def 집기_포즈(위치_세계, 요_도: float) -> np.ndarray:
    """손가락이 아래(-z)를 향하고, z축을 중심으로 요만큼 돌린 TCP 포즈(세계 기준 4×4)."""
    return 변환(Rz(요_도) @ Rx(180), 위치_세계)


def TCP_포즈(q) -> np.ndarray:
    """관절 각도(rad)에서 TCP의 세계 기준 포즈. 3장의 순기구학에 받침 위치를 곱한다."""
    return T_세계_받침 @ 순기구학(q, 손끝=손끝_집게)[-1]


def 포즈_오차(T_목표: np.ndarray, T_지금: np.ndarray) -> np.ndarray:
    """[위치 오차 3개(m), 자세 오차 회전 벡터 3개(rad)]. 3장 3.6절과 같다."""
    위치 = T_목표[:3, 3] - T_지금[:3, 3]
    자세 = Rotation.from_matrix(T_목표[:3, :3] @ T_지금[:3, :3].T).as_rotvec()
    return np.concatenate([위치, 자세])


def 역기구학(T_세계_목표: np.ndarray, q_시작, 반복: int = 100, λ: float = 0.05) -> np.ndarray:
    """3장의 감쇠 최소제곱(DLS)에 걸음 제한. 지금 자세에서 출발해 가까운 답을 찾는다."""
    T_받침_목표 = 역변환(T_세계_받침) @ T_세계_목표
    q = np.array(q_시작, dtype=float)
    for _ in range(반복):
        e = 포즈_오차(T_받침_목표, 순기구학(q, 손끝=손끝_집게)[-1])
        if np.linalg.norm(e) < 1e-6:
            break
        if np.linalg.norm(e) > 0.2:
            e = e * 0.2 / np.linalg.norm(e)
        J = 야코비안(q, 손끝=손끝_집게)
        q = q + J.T @ np.linalg.solve(J @ J.T + λ**2 * np.eye(6), e)
    return q


def 요_고르기(잡을_곳, 상자_요_도: float, q_지금) -> float:
    """집게는 앞뒤가 같으니 상자 요와 요+180도 둘 다 답이다. 손목3을 덜 돌리는 쪽을 고른다."""
    후보들 = [(상자_요_도 + 더할) % 360 - 180 for 더할 in (180, 0)]   # -180~180도로 정리
    돌림 = [abs(역기구학(집기_포즈(잡을_곳, 요), q_지금)[5] - q_지금[5]) for 요 in 후보들]
    return 후보들[int(np.argmin(돌림))]
