"""16장: 유니사이클 로봇의 비선형 MPC. 입력열을 SciPy SLSQP로 고르고, 장애물 여유 ≥ 0을 제약으로 건다."""
import numpy as np
from scipy.optimize import minimize

from 유니사이클 import 굴리기, 목표, 속도_한계, 여유, 회전_한계


def 비용(입력_한줄: np.ndarray, 상태: np.ndarray, N: int) -> float:
    """예측한 위치가 목표에서 먼 정도(마지막은 5배 더) + 회전을 많이 쓴 정도."""
    입력들 = 입력_한줄.reshape(N, 2)
    거리 = 굴리기(상태, 입력들)[:, :2] - 목표
    return float(np.sum(거리**2) + 5 * np.sum(거리[-1]**2) + 0.1 * np.sum(입력들[:, 1]**2))


def 계획(상태: np.ndarray, 첫_추측: np.ndarray) -> tuple[np.ndarray, int]:
    """지금 상태에서 N걸음 입력열((N,2))과 반복 횟수를 돌려준다."""
    N = len(첫_추측)
    결과 = minimize(비용, 첫_추측.ravel(), args=(상태, N), method="SLSQP",
                  bounds=[속도_한계, 회전_한계] * N,
                  constraints=[{"type": "ineq",          # 모든 예측 위치에서 모든 장애물과의 여유 ≥ 0
                                "fun": lambda U: 여유(굴리기(상태, U.reshape(N, 2))).ravel()}],
                  options={"maxiter": 100})
    return 결과.x.reshape(N, 2), 결과.nit
