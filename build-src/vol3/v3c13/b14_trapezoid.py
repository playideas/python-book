import matplotlib.pyplot as plt
import numpy as np

from 시간매기기 import 사다리꼴

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

v최대, a최대 = 1.0, 2.0                       # rad/s, rad/s²
그림, (위, 아래) = plt.subplots(2, 1, figsize=(6.5, 4.6), sharex=True)
for 거리, 색 in [(2.0, "tab:blue"), (0.3, "tab:orange")]:
    총시간, 간_거리 = 사다리꼴(거리, v최대, a최대)
    t = np.linspace(0, 총시간, 2001)
    s = 간_거리(t)
    v = np.gradient(s, t)
    a = np.gradient(v, t)
    print(f"거리 {거리}rad: {총시간:.3f}초, 가장 빠를 때 {v.max():.3f}rad/s, 가장 센 가속 {np.abs(a).max():.2f}rad/s²")
    위.plot(t, s, color=색, label=f"{거리}rad")
    아래.plot(t, v, color=색)
위.set_ylabel("간 거리 (rad)")
위.legend(fontsize=8)
아래.axhline(v최대, color="gray", linestyle=":")
아래.set_ylabel("속도 (rad/s)")
아래.set_xlabel("시간 (초)")
그림.tight_layout()
그림.savefig("trapezoid.png", dpi=200)
print("저장: trapezoid.png")
