import matplotlib.pyplot as plt
import numpy as np

from 진자장면 import 실행
from 피아이디 import PID

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

목표 = np.deg2rad(60)
그림, 칸 = plt.subplots(figsize=(7, 3.4))
for kp in [5, 15, 30]:
    기록 = 실행(PID(kp, 0, 0, 주기=0.01), 목표, 시간=4.0)
    각도_도 = np.rad2deg(기록["각도"])
    앞, 뒤 = 각도_도[:100], 각도_도[-100:]           # 처음 1초와 마지막 1초
    print(f"kp={kp:2d}: 처음 1초 {앞.min() + 0.0:5.1f}~{앞.max():5.1f}도, 마지막 1초 {뒤.min():5.1f}~{뒤.max():5.1f}도,"
          f" 흔들림의 가운데 {(뒤.min() + 뒤.max()) / 2:4.1f}도")
    칸.plot(기록["시각"], 각도_도, label=f"kp={kp}")
칸.axhline(60, color="gray", linestyle="--", linewidth=1)
칸.set_xlabel("시간(초)")
칸.set_ylabel("각도(도)")
칸.set_ylim(-100, 240)
칸.legend(fontsize=8, ncol=3, loc="upper left")
그림.tight_layout()
그림.savefig("p_only.png", dpi=200)
print("저장: p_only.png")
