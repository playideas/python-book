import matplotlib.pyplot as plt
import numpy as np

from 계단지표 import 계단_지표
from 실전PID import 실전PID
from 진자장면 import 실행

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

목표 = np.deg2rad(60)
kp들 = [10, 20, 30, 45, 60, 80]
kd들 = [1, 2, 3, 4, 6, 8, 10]
정착 = np.full((len(kp들), len(kd들)), np.nan)
오버슈트 = np.zeros_like(정착)
for i, kp in enumerate(kp들):
    for j, kd in enumerate(kd들):
        기록 = 실행(실전PID(kp, kp, kd, 주기=0.01), 목표, 시간=4.0)   # ki = kp로 묶어 두 칸만 훑는다
        지표 = 계단_지표(기록["시각"], 기록["각도"], 0.0, 목표)
        정착[i, j], 오버슈트[i, j] = 지표["정착"], 지표["오버슈트"]

가장_빠른 = np.unravel_index(np.nanargmin(정착), 정착.shape)
조건 = np.where(오버슈트 <= 5, 정착, np.nan)                  # 오버슈트 5% 이하만
가장_빠른_얌전한 = np.unravel_index(np.nanargmin(조건), 정착.shape)
for 이름, (i, j) in [("가장 빨리 정착", 가장_빠른), ("오버슈트 5% 이하 중 가장 빨리", 가장_빠른_얌전한)]:
    print(f"{이름}: kp={kp들[i]}, kd={kd들[j]} → 정착 {정착[i, j]:.2f}초, 오버슈트 {오버슈트[i, j]:.1f}%")
print(f"정착하지 못한 조합: {np.isnan(정착).sum()}개 / {정착.size}개")

그림, 칸 = plt.subplots(figsize=(7, 4))
그림판 = 칸.imshow(정착, cmap="viridis_r", vmin=0, vmax=3, origin="lower")
for i in range(len(kp들)):
    for j in range(len(kd들)):
        글 = "X" if np.isnan(정착[i, j]) else f"{정착[i, j]:.2f}\n{오버슈트[i, j]:.0f}%"
        칸.text(j, i, 글, ha="center", va="center", fontsize=7,
               color="black" if np.isnan(정착[i, j]) or 정착[i, j] < 1.5 else "white")
칸.set_xticks(range(len(kd들)), kd들)
칸.set_yticks(range(len(kp들)), kp들)
칸.set_xlabel("kd")
칸.set_ylabel("kp (ki = kp)")
그림.colorbar(그림판, label="정착 시간(초)")
그림.tight_layout()
그림.savefig("gain_grid.png", dpi=200)
print("저장: gain_grid.png")
