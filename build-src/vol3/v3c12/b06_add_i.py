import matplotlib.pyplot as plt
import numpy as np

from 계단지표 import 계단_지표, 지표_글
from 진자장면 import 실행
from 피아이디 import PID

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

목표 = np.deg2rad(60)
그림, 칸 = plt.subplots(figsize=(7, 3.4))
for ki in [0, 10, 30, 100]:
    기록 = 실행(PID(kp=30, ki=ki, kd=5.7, 주기=0.01), 목표, 시간=4.0)
    print(f"ki={ki:3d}: " + 지표_글(계단_지표(기록["시각"], 기록["각도"], 0.0, 목표)))
    칸.plot(기록["시각"], np.rad2deg(기록["각도"]), label=f"ki={ki}")
칸.axhline(60, color="gray", linestyle="--", linewidth=1)
칸.set_xlabel("시간(초)")
칸.set_ylabel("각도(도)")
칸.legend(fontsize=8, ncol=4, loc="lower right")
그림.tight_layout()
그림.savefig("add_i.png", dpi=200)
print("저장: add_i.png")
