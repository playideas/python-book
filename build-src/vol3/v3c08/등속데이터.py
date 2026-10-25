"""8.4절: 직선 위를 달리는 로봇과 10Hz 위치 센서(잡음 0.1m)."""
import numpy as np

주기 = 0.1
시간 = np.arange(0, 30, 주기)
참_속도 = 0.5 + 0.3 * np.sin(0.5 * 시간)                       # m/s
참_위치 = (0.5 * 시간 - 0.6 * np.cos(0.5 * 시간) + 0.6)         # 속도를 적분한 값(m)
측정 = 참_위치 + np.random.default_rng(1).normal(0, 0.1, len(시간))


def 등속_모델(q: float) -> tuple[np.ndarray, np.ndarray]:
    """상태 [위치, 속도]의 F와, 가속도가 세기 q로 아무렇게나 바뀐다고 본 Q."""
    F = np.array([[1, 주기], [0, 1]])
    Q = q * np.array([[주기**4 / 4, 주기**3 / 2], [주기**3 / 2, 주기**2]])
    return F, Q
