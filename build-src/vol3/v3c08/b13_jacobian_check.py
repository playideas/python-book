import numpy as np

from 바퀴로봇 import 움직이기, 움직임_야코비안, 표지_보기, 표지_야코비안


def 수치_야코비안(함수, 상태: np.ndarray, h: float = 1e-6) -> np.ndarray:
    """3장 3.5절처럼 하나씩 ±h만큼 움직여 본다(중앙 차분)."""
    열들 = []
    for i in range(len(상태)):
        d = np.zeros(len(상태))
        d[i] = h
        열들.append((함수(상태 + d) - 함수(상태 - d)) / (2 * h))
    return np.column_stack(열들)


상태 = np.array([1.0, 2.0, np.deg2rad(30)])
이동, 회전 = 0.2, np.deg2rad(10)
표지 = np.array([3.0, 1.0])

F, _ = 움직임_야코비안(상태, 이동, 회전)
F_수치 = 수치_야코비안(lambda s: 움직이기(s, 이동, 회전), 상태)
H = 표지_야코비안(상태, 표지)
H_수치 = 수치_야코비안(lambda s: 표지_보기(s, 표지), 상태)
print("F 공식:\n", np.round(F, 4) + 0.0)
print("F 공식과 수치의 가장 큰 차이:", f"{np.abs(F - F_수치).max():.1e}")
print("H 공식:\n", np.round(H, 4) + 0.0)
print("H 공식과 수치의 가장 큰 차이:", f"{np.abs(H - H_수치).max():.1e}")
