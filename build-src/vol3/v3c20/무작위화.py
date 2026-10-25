"""20.4절: 물성을 무작위로 흔들어 만든 팔 여러 대에서 이득을 고른다."""
import numpy as np

from 팔제어 import 돌려_보기
from 현실팔 import 물성

kp들, kd들 = [20, 30, 40, 60, 80, 110], [1, 2, 3, 4, 6, 8]


def 무작위_물성(생성기: np.random.Generator, 폭: float = 1.0) -> 물성:
    """시뮬 값을 가운데 두고 흔든다. 폭 0이면 시뮬 그대로, 폭이 클수록 넓게."""
    return 물성(끝_질량=0.4 * 생성기.uniform(1 - 0.5 * 폭, 1 + 폭),
              감쇠=0.5 * 생성기.uniform(1 - 0.6 * 폭, 1 + 0.6 * 폭),
              마찰=생성기.uniform(0, 0.3 * 폭),
              토크_배율=생성기.uniform(1 - 0.2 * 폭, 1 + 0.1 * 폭),
              지연=int(생성기.integers(0, round(2 * 폭) + 1)),          # 0 ~ 2×폭 틱
              잡음=np.deg2rad(생성기.uniform(0, 0.4 * 폭)),
              유격=np.deg2rad(생성기.uniform(0, 0.8 * 폭)))


def 점수표(아는: 물성, 팔들: list[물성]) -> np.ndarray:
    """이득 칸마다, 팔 여러 대에서 돌린 평균 오차(도)의 평균."""
    return np.array([[np.mean([돌려_보기(kp, kd, 아는, 팔, 시드)[0] for 시드, 팔 in enumerate(팔들)])
                      for kd in kd들] for kp in kp들])


def 가장_좋은_칸(표: np.ndarray) -> tuple[int, int]:
    i, j = np.unravel_index(np.argmin(표), 표.shape)
    return kp들[i], kd들[j]
