import numpy as np

# 직선 맞추기: 전압(V)을 넣었을 때 모터 속도(rad/s)를 쟀다. 속도 = a·전압 + b 로 맞춘다
rng = np.random.default_rng(0)
전압 = np.linspace(1, 12, 12)
속도 = 18.0 * 전압 - 5.0 + rng.normal(0, 3.0, 전압.size)          # 참값 a=18, b=-5에 잡음
X = np.column_stack([전압, np.ones_like(전압)])                   # 열마다 모르는 값 하나
(a, b), 잔차, *_ = np.linalg.lstsq(X, 속도, rcond=None)
print(f"lstsq: a = {a:.3f}, b = {b:.3f}, 잔차 제곱합 {잔차[0]:.2f}")
print("정규 방정식 (XᵀX)⁻¹Xᵀy:", np.round(np.linalg.solve(X.T @ X, X.T @ 속도), 3))
