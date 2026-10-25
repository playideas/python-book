import time

import matplotlib.pyplot as plt
import mujoco
import numpy as np

from MPPI도구 import MPPI
from 진자장면 import 세운_자세_오차, 장면

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

모델, 진짜 = 장면()
제어기 = MPPI(모델, 후보_수=128, 걸음_수=100)              # 후보 128개 × 1초 앞
각도들, 토크들, 걸린_시간 = [], [], []
for _ in range(600):                                     # 6초, 100Hz
    시작 = time.perf_counter()
    진짜.ctrl[0] = 제어기.고르기(진짜)
    걸린_시간.append(time.perf_counter() - 시작)
    mujoco.mj_step(모델, 진짜)                            # 진짜 진자는 고른 첫 입력으로 한 걸음
    각도들.append(진짜.qpos[0])
    토크들.append(진짜.ctrl[0])
시각 = np.arange(1, 601) * 모델.opt.timestep
오차_도 = np.rad2deg(np.abs(세운_자세_오차(np.array(각도들))))
print(f"처음으로 거꾸로 선 자세 10도 안에 든 시각: {시각[np.argmax(오차_도 < 10)]:.2f}초")
print(f"마지막 2초 동안 가장 큰 오차: {오차_도[-200:].max():.1f}도")
print(f"한 주기 계획 시간(이 맥): 중앙값 {np.median(걸린_시간) * 1000:.1f}ms, 제어 주기 {모델.opt.timestep * 1000:.0f}ms")

그림, (칸1, 칸2) = plt.subplots(2, 1, figsize=(7, 4.2), sharex=True)
칸1.plot(시각, np.rad2deg(각도들))
for 높이 in (180, -180):
    칸1.axhline(높이, color="gray", linestyle="--", linewidth=1)
칸1.set_ylabel("각도(도)")
칸1.set_yticks([-180, -90, 0, 90, 180])
칸2.plot(시각, 토크들, linewidth=0.8)
칸2.set_ylabel("토크(N·m)")
칸2.set_xlabel("시간(초)")
그림.tight_layout()
그림.savefig("mppi_swingup.png", dpi=200)
print("저장: mppi_swingup.png")
