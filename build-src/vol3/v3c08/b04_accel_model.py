import numpy as np

g = 9.81


def h(피치: float) -> np.ndarray:
    """측정 모델: 가만히 있을 때 가속도계가 재는 [x, z](m/s²)."""
    return np.array([-g * np.sin(피치), g * np.cos(피치)])


생성기 = np.random.default_rng(0)
참_피치 = np.deg2rad(20.0)
가속도_잡음 = 0.5                                       # m/s²
잰_값 = h(참_피치) + 생성기.normal(0, 가속도_잡음, (10000, 2))    # z = h(x) + 잡음
읽은_피치 = np.arctan2(-잰_값[:, 0], 잰_값[:, 1])

print("h(20도) =", np.round(h(참_피치), 3))
print(f"읽은 피치: 평균 {np.rad2deg(읽은_피치.mean()):.2f}도, 표준편차 {np.rad2deg(읽은_피치.std()):.2f}도")
print(f"어림셈 잡음/g = {np.rad2deg(가속도_잡음 / g):.2f}도")
