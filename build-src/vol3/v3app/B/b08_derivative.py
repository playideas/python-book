import numpy as np


def f(t: float) -> float:
    return np.sin(t)                    # 위치가 sin(t)로 움직이면 속도는 cos(t)


t, 참값 = 1.0, np.cos(1.0)
for h in [1e-1, 1e-3, 1e-5]:
    전진 = (f(t + h) - f(t)) / h                      # 앞으로 한 칸
    중앙 = (f(t + h) - f(t - h)) / (2 * h)            # 앞뒤로 한 칸씩(3장)
    print(f"h={h:.0e}: 전진 차분 오차 {abs(전진 - 참값):.1e}, 중앙 차분 오차 {abs(중앙 - 참값):.1e}")

# 기록된 신호에서 속도 구하기: np.gradient는 안쪽은 중앙 차분, 양 끝은 한쪽 차분
시각 = np.arange(0, 0.5, 0.1)
print("np.gradient(sin) :", np.round(np.gradient(np.sin(시각), 0.1), 4))
print("참값 cos         :", np.round(np.cos(시각), 4))
