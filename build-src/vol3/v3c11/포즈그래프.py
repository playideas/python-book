"""11장: 포즈 그래프를 최소 제곱으로 펴는 도구."""
import numpy as np
from scipy.optimize import least_squares

from 포즈도구 import 각도_정리


def 상대_포즈들(포즈들: np.ndarray, 가: np.ndarray, 나: np.ndarray) -> np.ndarray:
    """간선 여러 개를 한꺼번에: 포즈들[가]에서 본 포즈들[나]의 (x, y, 각)."""
    차이 = 포즈들[나, :2] - 포즈들[가, :2]
    c, s = np.cos(포즈들[가, 2]), np.sin(포즈들[가, 2])
    return np.column_stack([c * 차이[:, 0] + s * 차이[:, 1],      # 가의 방향으로 돌려 적기(Rᵀ @ 차이)
                            -s * 차이[:, 0] + c * 차이[:, 1],
                            각도_정리(포즈들[나, 2] - 포즈들[가, 2])])


def 그래프_펴기(처음_포즈들: np.ndarray, 간선들: list, 위치_시그마: float = 0.05,
             각_시그마: float = 0.02) -> np.ndarray:
    """간선 (가, 나, 잰 상대 포즈)들을 가장 잘 만족하는 포즈들. 0번 포즈는 움직이지 않는다."""
    가 = np.array([e[0] for e in 간선들])
    나 = np.array([e[1] for e in 간선들])
    잰_값 = np.array([e[2] for e in 간선들])
    무게 = np.array([1 / 위치_시그마, 1 / 위치_시그마, 1 / 각_시그마])

    def 잔차(변수: np.ndarray) -> np.ndarray:
        포즈들 = np.vstack([처음_포즈들[:1], 변수.reshape(-1, 3)])
        차 = 상대_포즈들(포즈들, 가, 나) - 잰_값
        차[:, 2] = 각도_정리(차[:, 2])                          # 359도 차이는 1도 차이다
        return (차 * 무게).ravel()

    결과 = least_squares(잔차, 처음_포즈들[1:].ravel())
    return np.vstack([처음_포즈들[:1], 결과.x.reshape(-1, 3)])
