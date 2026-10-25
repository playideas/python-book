import matplotlib.pyplot as plt
import numpy as np

import 페테크 as ft
from 가짜서보 import 가상시계, 가짜버스, 가짜서보
from 서보통신 import 서보버스

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

도_눈금 = 4096 / 360
주기 = 0.02                                       # 50Hz
한계_눈금 = round(5 * 도_눈금)                     # 한 번에 현재 위치에서 5도까지만 앞서게

시계 = 가상시계()
가짜 = 가짜버스([가짜서보(i, 실제_위치=2047) for i in (1, 2, 3)], 시계)
버스 = 서보버스(가짜.포트_이름, 속도=115_200)
for i in (1, 2, 3):
    버스.쓰기(i, ft.토크_켜기, 1)

기록 = []
for k in range(100):                              # 2초
    t = k * 주기
    현재 = 버스.함께_읽기(ft.현재_위치, [1, 2, 3])  # 1) 재고
    원하는_1_2 = 2047 + round(90 * 도_눈금) * (t >= 0.1)          # 0.1초에 90도로 한 번에
    제한된 = 현재[2] + np.clip(원하는_1_2 - 현재[2], -한계_눈금, 한계_눈금)
    원하는_3 = 2047 + round(30 * 도_눈금 * np.sin(2 * np.pi * 1.0 * t))  # 1Hz로 ±30도
    버스.함께_쓰기(ft.목표_위치, {1: 원하는_1_2, 2: int(제한된), 3: 원하는_3})   # 2) 보내고
    기록.append([t, 원하는_1_2, 현재[1], 현재[2], 원하는_3, 현재[3]])
    시계.진행(주기)                                # 3) 다음 박자까지

기록 = np.array(기록, dtype=float)
기록[:, 1:] = (기록[:, 1:] - 2047) / 도_눈금        # 눈금 → 도
시간 = 기록[:, 0]
for 이름, 열 in [("한 번에", 2), ("5도씩 제한", 3)]:
    도착 = 시간[np.argmax(기록[:, 열] >= 89)]
    최대_속도 = np.max(np.diff(기록[:, 열])) / 주기
    print(f"{이름}: 89도 도착 {도착 - 0.1:.2f}초 뒤, 가장 빠를 때 초당 {최대_속도:.0f}도")
# 뒤쪽 1초의 읽은 값을 A·sin(ωt - φ)로 맞춰 보면 늦음 φ/ω와 크기 A를 알 수 있다
ω = 2 * np.pi * 1.0
뒤 = 시간 >= 1.0
사인, 코사인 = np.linalg.lstsq(np.c_[np.sin(ω * 시간[뒤]), np.cos(ω * 시간[뒤])], 기록[뒤, 5], rcond=None)[0]
print(f"1Hz 사인: 크기 {np.hypot(사인, 코사인):.1f}도(목표 30도), 목표보다 {np.arctan2(-코사인, 사인) / ω * 1000:.0f}ms 늦다")

그림, 칸들 = plt.subplots(1, 2, figsize=(9, 3.4))
칸들[0].step(시간, 기록[:, 1], where="post", color="gray", linestyle="--", label="원하는 각도")
칸들[0].plot(시간, 기록[:, 2], ".-", markersize=3, label="한 번에 보냄")
칸들[0].plot(시간, 기록[:, 3], ".-", markersize=3, label="5도씩 제한")
칸들[1].plot(시간, 기록[:, 4], color="gray", linestyle="--", label="목표")
칸들[1].plot(시간, 기록[:, 5], ".-", markersize=3, label="읽은 위치")
for 칸, 제목 in zip(칸들, ["90도 계단", "1Hz 사인"]):
    칸.set_title(제목)
    칸.set_xlabel("시간(초)")
    칸.set_ylabel("각도(도)")
    칸.legend(fontsize=8)
그림.tight_layout()
그림.savefig("servo_loop.png", dpi=200)
print("저장: servo_loop.png")
