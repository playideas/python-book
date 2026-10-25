import numpy as np

R = 0.02**2
참값 = np.where(np.arange(200) < 100, 1.0, 0.8)     # 100번째 측정부터 벽이 0.2m 가까워진다
측정 = 참값 + np.random.default_rng(0).normal(0, 0.02, 200)

print("    Q     | 1cm 안으로 들어오기 | 마지막 40번의 흔들림 | 안정된 K")
for Q in [0.0, 1e-6, 1e-5, 1e-4, 1e-3]:
    x, P, 추정 = 0.0, 100.0, []
    for z in 측정:
        P = P + Q
        K = P / (P + R)
        x = x + K * (z - x)
        P = (1 - K) * P
        추정.append(x)
    오차 = np.abs(np.array(추정[100:]) - 0.8)
    if (오차 < 0.01).any():
        따라잡기 = f"{np.argmax(오차 < 0.01) + 1:3d}번 만에"
        흔들림 = f"{np.std(추정[160:]) * 1000:5.1f}mm"
    else:
        따라잡기, 흔들림 = "못 들어옴", "-"
    print(f" {Q:8.0e} | {따라잡기:>12s} | {흔들림:>10s} | {K:.3f}")
