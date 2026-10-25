"""20.3절: 기록과 같은 토크를 후보 모델에 넣어 보고, 궤적이 가장 잘 겹치는 물성을 최소제곱으로 찾는다."""
from collections.abc import Callable

import numpy as np
from scipy.optimize import least_squares

from 현실팔 import 물성, 실행

이름들 = ["끝_질량", "감쇠", "마찰", "토크_배율"]
처음값 = [0.4, 0.5, 0.0, 1.0]                       # 시뮬 물성에서 출발
아래, 위 = [0.05, 0.0, 0.0, 0.3], [2.0, 3.0, 2.0, 2.0]   # 말이 되는 범위


def 맞추기(토크: Callable, 기록: dict, 지연: int) -> tuple[물성, float]:
    """지연(정수)을 고정하고 연속값 네 개를 찾는다. 맞춘 물성과 남은 차이 RMS(도)를 돌려준다."""
    시간 = len(기록["시각"]) * (기록["시각"][1] - 기록["시각"][0])

    def 차이(x: np.ndarray) -> np.ndarray:
        후보 = 물성(**dict(zip(이름들, x)), 지연=지연)
        return (실행(토크, 시간, 후보)["잰_각도"] - 기록["잰_각도"]).ravel()

    결과 = least_squares(차이, 처음값, bounds=(아래, 위), diff_step=1e-3)
    return 물성(**dict(zip(이름들, 결과.x)), 지연=지연), float(np.rad2deg(np.sqrt(np.mean(결과.fun ** 2))))


def 식별(토크: Callable, 기록: dict, 지연_후보: range = range(5), 보이기: bool = True) -> tuple[물성, float]:
    """정수인 지연은 하나씩 다 해 보고(격자), 남은 차이가 가장 작은 것을 고른다."""
    결과들 = [맞추기(토크, 기록, d) for d in 지연_후보]
    for p, rms in 결과들 if 보이기 else []:
        print(f"  지연 {p.지연}틱: " + ", ".join(f"{이름} {getattr(p, 이름):.3f}" for 이름 in 이름들)
              + f" → 남은 차이 {rms:.2f}도")
    return min(결과들, key=lambda 짝: 짝[1])
