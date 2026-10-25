import matplotlib.pyplot as plt
import numpy as np

import 페테크 as ft
import 가상팔
from 궤적 import 목표_자세

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

시계, 가짜, 버스 = 가상팔.만들기()
가상팔.보정하기(버스, 가짜)
아이디들 = 가상팔.아이디들
버스.함께_쓰기(ft.목표_위치, 버스.함께_읽기(ft.현재_위치, 아이디들))   # 켜기 전에 목표 = 지금 위치
for i in 아이디들:
    버스.쓰기(i, ft.토크_켜기, 1)

주기 = 0.02
시간, 목표들, 읽은들, 참들 = [], [], [], []
for k in range(round(6.5 / 주기)):
    t = k * 주기
    읽은 = 가상팔.눈금_각도(버스.함께_읽기(ft.현재_위치, 아이디들))
    목표 = 목표_자세(t)
    버스.함께_쓰기(ft.목표_위치, 가상팔.각도_눈금(목표))
    시간.append(t), 목표들.append(목표), 읽은들.append(읽은), 참들.append(가상팔.참_각도(가짜))
    시계.진행(주기)

시간, 목표들, 읽은들, 참들 = map(np.array, (시간, 목표들, 읽은들, 참들))
print(f"{len(시간)}주기 동안 실패 없이 돌았다. 통계: {버스.통계}")
print(f"읽은 각도와 참 각도의 최대 차이: {np.abs(읽은들 - 참들).max():.3f}도")
따라가기_오차 = np.abs(읽은들[1:] - 목표들[:-1]).max(axis=0)
for 이름, 오차 in zip(가상팔.관절들, 따라가기_오차):
    print(f"  {이름:14s} 한 주기 전 목표와의 최대 차이 {오차:5.1f}도")
print("마지막 자세(도):", np.round(읽은들[-1], 1) + 0.0)

그림, 칸들 = plt.subplots(2, 3, figsize=(10, 5), sharex=True)
for j, 칸 in enumerate(칸들.flat):
    칸.plot(시간, 목표들[:, j], color="gray", linestyle="--", label="목표")
    칸.plot(시간, 읽은들[:, j], color="tab:blue", label="읽은 각도")
    칸.set_title(f"{가상팔.아이디들[j]}번 {가상팔.관절들[j]}", fontsize=10)
for 칸 in 칸들[1]:
    칸.set_xlabel("시간(초)")
for 칸 in 칸들[:, 0]:
    칸.set_ylabel("각도(도)")
칸들[0, 0].legend(fontsize=8)
그림.tight_layout()
그림.savefig("so101_wave.png", dpi=200)
print("저장: so101_wave.png")
