"""7.12절 실습: 시각 t(초)에 팔이 있어야 할 관절 각도(도)."""
import numpy as np

쉬는_자세 = np.array([0, -95, 90, 70, 0, 0], dtype=float)
준비_자세 = np.array([30, -20, 30, 50, 0, 40], dtype=float)


def _부드럽게(u: float) -> float:
    """0에서 1로 가는 동안 처음과 끝이 느린 S자 곡선."""
    u = min(max(u, 0.0), 1.0)
    return (1 - np.cos(np.pi * u)) / 2


def 목표_자세(t: float) -> np.ndarray:
    if t < 1.5:                                    # 쉬는 자세 → 준비 자세
        return 쉬는_자세 + (준비_자세 - 쉬는_자세) * _부드럽게(t / 1.5)
    if t < 4.5:                                    # 손목을 돌리며 손 흔들기
        자세 = 준비_자세.copy()
        자세[4] = 45 * np.sin(2 * np.pi * (t - 1.5) / 2.0)
        return 자세
    return 준비_자세 + (쉬는_자세 - 준비_자세) * _부드럽게((t - 4.5) / 1.5)
