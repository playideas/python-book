"""14장: 차동 구동 로봇의 기구학. 포즈는 지도 기준 (x, y, θ)(m, m, rad)."""
import numpy as np

바퀴_반지름 = 0.05      # m
바퀴_간격 = 0.26        # m. 두 바퀴 사이 거리(8장 로봇과 같은 치수)


def 각도_감싸기(각):
    """각도를 -π 이상 π 미만으로 접는다."""
    return (np.asarray(각) + np.pi) % (2 * np.pi) - np.pi


def 바퀴에서_속도(왼_각속도: float, 오른_각속도: float) -> tuple[float, float]:
    """두 바퀴의 각속도(rad/s)를 몸의 선속도 v(m/s)와 각속도 ω(rad/s)로."""
    왼, 오른 = 왼_각속도 * 바퀴_반지름, 오른_각속도 * 바퀴_반지름   # 바퀴 둘레의 속도(m/s)
    return (왼 + 오른) / 2, (오른 - 왼) / 바퀴_간격


def 속도에서_바퀴(v: float, ω: float) -> tuple[float, float]:
    """원하는 v, ω를 내려면 두 바퀴를 몇 rad/s로 돌려야 하나."""
    return (v - ω * 바퀴_간격 / 2) / 바퀴_반지름, (v + ω * 바퀴_간격 / 2) / 바퀴_반지름


def 유니사이클_걸음(포즈, v: float, ω: float, dt: float) -> np.ndarray:
    """v, ω를 dt초 동안 유지했을 때의 다음 포즈. 도는 동안에는 원호를 따라 정확히 옮긴다."""
    x, y, θ = 포즈
    if abs(ω) < 1e-9:
        return np.array([x + v * dt * np.cos(θ), y + v * dt * np.sin(θ), θ])
    반지름 = v / ω
    새_θ = θ + ω * dt
    return np.array([x + 반지름 * (np.sin(새_θ) - np.sin(θ)),
                     y - 반지름 * (np.cos(새_θ) - np.cos(θ)),
                     float(각도_감싸기(새_θ))])
