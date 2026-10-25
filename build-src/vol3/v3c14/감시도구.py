"""14장: 도착 판정과 진척 감시. 값은 Nav2 문서의 기본값(0.25m, 0.5m/10초)을 따랐다."""
import numpy as np


def 도착했나(포즈, 목표, 거리_허용: float = 0.25) -> bool:
    """목표 위치에서 거리_허용(m) 안이면 도착. 이 장의 목적지는 방향을 따지지 않는다."""
    return bool(np.hypot(목표[0] - 포즈[0], 목표[1] - 포즈[1]) <= 거리_허용)


class 진척_감시:
    """허용_초 동안 기준 반지름(m)만큼도 못 움직였으면 '막혔다'고 알린다."""

    def __init__(self, 반지름: float = 0.5, 허용_초: float = 10.0) -> None:
        self.반지름, self.허용_초 = 반지름, 허용_초
        self.기준_위치, self.기준_시각 = None, 0.0

    def 다시(self, 위치, 시각: float) -> None:
        self.기준_위치, self.기준_시각 = np.array(위치[:2], dtype=float), 시각

    def 막혔나(self, 위치, 시각: float) -> bool:
        if self.기준_위치 is None or np.linalg.norm(np.asarray(위치[:2]) - self.기준_위치) > self.반지름:
            self.다시(위치, 시각)                  # 충분히 움직였으면 기준을 지금으로 옮긴다
            return False
        return 시각 - self.기준_시각 > self.허용_초
