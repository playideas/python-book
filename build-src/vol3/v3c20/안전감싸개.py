"""20.7절: 어떤 제어기든 모터 바로 앞에서 감싸 한계를 지키고, 이상하면 힘을 빼는 안전층."""
from collections import deque
from collections.abc import Callable

import numpy as np

from 현실팔 import 주기, 토크_한계


class 안전감싸개:
    def __init__(self, 제어기: Callable, 각도_범위: np.ndarray, 토크_비율: float = 0.5,
                 속도_한계: float = 3.0, 토크_변화_한계: float = 0.5):
        self.제어기 = 제어기
        self.각도_범위 = 각도_범위                  # 관절마다 (아래, 위) rad. 7장 서보의 위치 한계와 같은 울타리
        self.토크_상한 = 토크_비율 * 토크_한계     # 처음에는 모터 힘의 일부만 쓴다
        self.속도_한계 = 속도_한계                  # rad/s, 이보다 빨리 돌면 멈춘다
        self.토크_변화_한계 = 토크_변화_한계        # 한 주기에 토크가 바뀔 수 있는 크기(N·m)
        self.지난_각도들 = deque(maxlen=5)          # 속도는 5주기(0.05초) 사이로 재서 잡음에 덜 흔들린다
        self.이전_토크 = np.zeros(2)
        self.멈춘_시각, self.멈춘_까닭 = None, ""

    def 멈추기(self, t: float, 까닭: str) -> np.ndarray:
        if self.멈춘_시각 is None:
            self.멈춘_시각, self.멈춘_까닭 = t, 까닭
        return np.zeros(2)                          # 힘 빼기. 한 번 멈추면 사람이 다시 켤 때까지 그대로

    def __call__(self, t: float, 잰_각도: np.ndarray) -> np.ndarray:
        if self.멈춘_시각 is not None or not np.all(np.isfinite(잰_각도)):
            return self.멈추기(t, "멈춘 상태 또는 센서 값 없음")
        if np.any(잰_각도 < self.각도_범위[:, 0]) or np.any(잰_각도 > self.각도_범위[:, 1]):
            return self.멈추기(t, "관절 범위 밖")
        if len(self.지난_각도들) == self.지난_각도들.maxlen:
            속도 = (잰_각도 - self.지난_각도들[0]) / (len(self.지난_각도들) * 주기)
            if np.any(np.abs(속도) > self.속도_한계):
                return self.멈추기(t, "너무 빠름")
        self.지난_각도들.append(잰_각도.copy())
        토크 = np.clip(self.제어기(t, 잰_각도), -self.토크_상한, self.토크_상한)
        토크 = self.이전_토크 + np.clip(토크 - self.이전_토크, -self.토크_변화_한계, self.토크_변화_한계)
        self.이전_토크 = 토크
        return 토크
