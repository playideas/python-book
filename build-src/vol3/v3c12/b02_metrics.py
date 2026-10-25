import matplotlib.pyplot as plt
import numpy as np

from 계단지표 import 계단_지표, 지표_글
from 진자장면 import 실행
from 피아이디 import PID

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

목표 = np.deg2rad(60)
기록 = 실행(PID(kp=30, ki=30, kd=3, 주기=0.01), 목표, 시간=2.0)
지표 = 계단_지표(기록["시각"], 기록["각도"], 0.0, 목표)
print(지표_글(지표))

시각, 각도_도 = 기록["시각"], np.rad2deg(기록["각도"])
그림, 칸 = plt.subplots(figsize=(7, 3.4))
칸.plot(시각, 각도_도, color="tab:blue", label="진자 각도")
칸.axhline(60, color="gray", linestyle="--", linewidth=1, label="목표 60도")
칸.axhspan(60 * 0.98, 60 * 1.02, color="tab:green", alpha=0.15, label="±2% 띠")
for 비율 in [0.1, 0.9]:
    t = 시각[np.argmax(각도_도 >= 60 * 비율)]
    칸.plot(t, 60 * 비율, "ko", markersize=4)
    칸.annotate(f"{비율:.0%}", (t, 60 * 비율), xytext=(6, -10), textcoords="offset points", fontsize=8)
꼭대기 = np.argmax(각도_도)
칸.annotate(f"오버슈트 {지표['오버슈트']:.1f}%", (시각[꼭대기], 각도_도[꼭대기]), xytext=(20, 0),
           textcoords="offset points", fontsize=9, arrowprops={"arrowstyle": "->"})
칸.axvline(지표["정착"], color="tab:green", linestyle=":", label=f"정착 {지표['정착']:.2f}초")
칸.set_xlabel("시간(초)")
칸.set_ylabel("각도(도)")
칸.legend(fontsize=8, loc="lower right")
그림.tight_layout()
그림.savefig("step_metrics.png", dpi=200)
print("저장: step_metrics.png")
