import numpy as np
from scipy.optimize import brentq

목표 = np.deg2rad(60)


def 중력_토크(각도: float) -> float:
    """4장 진자(0.5m 막대 끝 1kg 추, 막대 0.01kg)를 아래로 돌리려는 중력 토크(N·m)."""
    return 9.81 * (1.0 * 0.5 + 0.01 * 0.25) * np.sin(각도)


for kp, 잰_값_도 in [(5, 30.9), (20, 49.3), (100, 57.6)]:
    # 용수철이 미는 힘 kp × (목표 - 각도)와 중력 토크가 비기는 각도를 찾는다
    멈춘_각도 = brentq(lambda 각도: kp * (목표 - 각도) - 중력_토크(각도), 0, 목표)
    print(f"kp={kp:3d}: 식으로 {np.rad2deg(멈춘_각도):4.1f}도, 4장에서 잰 값 {잰_값_도}도"
          f" → 처짐 {60 - np.rad2deg(멈춘_각도):4.1f}도, 그때 모터 토크 {중력_토크(멈춘_각도):.2f}N·m")
