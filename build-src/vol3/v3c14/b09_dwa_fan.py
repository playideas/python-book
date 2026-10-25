import matplotlib.pyplot as plt
import numpy as np

from 동적창 import dwa, 최고_v, 최고_ω, 후보_굴리기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# 로봇은 원점에서 +x를 보고 0.4m/s로 달리는 중. 1.1m 앞에 반지름 0.25m 기둥, 목표점은 2.5m 앞
각 = np.linspace(0, 2 * np.pi, 40, endpoint=False)
기둥 = np.column_stack([1.1 + 0.25 * np.cos(각), 0.05 + 0.25 * np.sin(각)])
결과 = dwa(np.zeros(3), 0.4, 0.0, np.array([2.5, 0.0]), 기둥)
가능 = 결과["가능"]
print(f"창 안의 후보 {len(가능)}개 중 버린 것 {np.sum(~가능)}개")
print(f"고른 명령: v {결과['v']:.3f}m/s, ω {결과['ω']:.3f}rad/s")

그림, 칸 = plt.subplots(figsize=(7, 4))
# 회색: 가속 한계를 무시하면 낼 수 있었을 모든 속도. 0.1초 안에는 이 중 일부만 낼 수 있다
v들, ω들 = (a.ravel() for a in np.meshgrid(np.linspace(0, 최고_v, 6), np.linspace(-최고_ω, 최고_ω, 13)))
for 궤 in 후보_굴리기(np.zeros(3), v들, ω들):
    칸.plot(궤[:, 0], 궤[:, 1], color="0.8", lw=0.6)
for 궤, 됨 in zip(결과["궤적"], 가능):
    칸.plot(궤[:, 0], 궤[:, 1], color="tab:green" if 됨 else "tab:red", lw=0.8)
최선 = 결과["궤적"][결과["최선"]]
칸.plot(최선[:, 0], 최선[:, 1], color="tab:blue", lw=2.5, label="고른 궤적")
칸.fill(기둥[:, 0], 기둥[:, 1], color="0.3")
칸.plot(2.5, 0, "k*", ms=12, label="목표점")
칸.plot([], [], color="0.8", label="가속 한계 밖의 속도")
칸.plot([], [], color="tab:red", label="창 안, 버린 후보")
칸.plot([], [], color="tab:green", label="창 안, 가능한 후보")
칸.set(aspect="equal", xlim=(-0.6, 2.7), xlabel="x(m)", ylabel="y(m)")
칸.legend(fontsize=8, loc="upper left", bbox_to_anchor=(1.01, 1))
그림.tight_layout()
그림.savefig("dwa_fan.png", dpi=200)
print("저장: dwa_fan.png")
