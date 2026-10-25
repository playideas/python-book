import matplotlib.pyplot as plt
import numpy as np

from LQR도구 import LQR
from 이중적분기 import A, B, 주기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

Q = np.diag([1.0, 0.1])
x0 = np.array([-1.0, 0.0])
시각 = np.arange(61) * 주기
그림, (칸1, 칸2) = plt.subplots(1, 2, figsize=(8.5, 3.2))
for R in [0.01, 0.1, 1.0]:
    K, _ = LQR(A, B, Q, R)
    x, 위치, 입력 = x0.copy(), [x0[0]], []
    for _ in range(60):
        u = float((-K @ x)[0])                     # LQR은 상태에 이득을 곱하기만 하면 된다
        x = A @ x + B[:, 0] * u
        위치.append(x[0])
        입력.append(u)
    위치 = np.array(위치)
    도착 = 시각[np.argmax(np.abs(위치) < 0.02)]
    print(f"R={R:4}: K={np.round(K[0], 2)} | 2cm 안에 드는 시각 {도착:.1f}초, "
          f"가장 센 입력 {max(np.abs(입력)):.2f}m/s², 지나침 {max(위치.max(), 0) * 100:.1f}cm")
    칸1.plot(시각, 위치, label=f"R={R}")
    칸2.step(시각[:-1], 입력, where="post", label=f"R={R}")
칸1.axhline(0, color="gray", linestyle="--", linewidth=1)
칸1.set_ylabel("위치(m)")
칸2.set_ylabel("입력: 가속도(m/s²)")
for 칸 in (칸1, 칸2):
    칸.set_xlabel("시간(초)")
    칸.legend(fontsize=8)
그림.tight_layout()
그림.savefig("lqr_weights.png", dpi=200)
print("저장: lqr_weights.png")
