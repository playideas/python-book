import matplotlib.pyplot as plt
import numpy as np

import 페테크 as ft
import 가상팔
from 궤적 import 목표_자세
from 서보통신 import 통신실패

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

주기, 감시_한계 = 0.02, 0.1                 # 새 측정 없이 0.1초가 지나면 멈춘다
아이디들 = 가상팔.아이디들


def 돌리기(감시견: bool) -> tuple[np.ndarray, np.ndarray, float | None]:
    시계, 가짜, 버스 = 가상팔.만들기(씨앗=7)
    가상팔.보정하기(버스, 가짜)
    # 보정을 마친 뒤 선이 나빠진다: 응답 3% 손실, 2% 깨짐, 2.0~2.6초에는 선이 아예 빠진다
    가짜.손실률, 가짜.깨짐률, 가짜.끊김 = 0.03, 0.02, (2.0, 2.6)
    버스.함께_쓰기(ft.목표_위치, 버스.함께_읽기(ft.현재_위치, 아이디들))
    for i in 아이디들:
        버스.쓰기(i, ft.토크_켜기, 1)
    마지막_성공, 멈춘_시각, 실패_주기, 참들 = 0.0, None, 0, []
    for k in range(round(6.5 / 주기)):
        t = k * 주기
        try:
            읽음 = 버스.함께_읽기(ft.현재_위치, 아이디들)
            마지막_성공 = t
        except 통신실패:
            읽음 = None
            실패_주기 += 1
        if 감시견 and 멈춘_시각 is None and t - 마지막_성공 >= 감시_한계:
            멈춘_시각 = t                           # 측정이 너무 오래됐다: 새 목표를 그만 보낸다
            print(f"  [!] {t:.2f}초: 마지막 측정({마지막_성공:.2f}초) 뒤 {감시_한계}초가 지나 멈춤")
        if 멈춘_시각 is None:
            버스.함께_쓰기(ft.목표_위치, 가상팔.각도_눈금(목표_자세(t)))
        elif 읽음 is not None:
            버스.함께_쓰기(ft.목표_위치, 읽음)       # 멈춘 뒤 연결이 돌아오면 지금 자리에서 버틴다
        참들.append(가상팔.참_각도(가짜))
        시계.진행(주기)
    print(f"  실패한 주기 {실패_주기}개, 통계 {버스.통계}")
    참들 = np.array(참들)
    속도 = np.abs(np.diff(참들, axis=0)).max(axis=1) / 주기   # 주기마다 가장 빨랐던 관절의 속도
    return 참들, 속도, 멈춘_시각


시간 = np.arange(round(6.5 / 주기)) * 주기
그림, 칸들 = plt.subplots(1, 2, figsize=(10, 3.4))
for 감시견 in [False, True]:
    print(f"감시견 {'켬' if 감시견 else '끔'}")
    참들, 속도, 멈춘_시각 = 돌리기(감시견)
    print(f"  가장 빠른 관절 속도: 끊기기 전 초당 {속도[시간[1:] < 2.0].max():.0f}도, "
          f"연결이 돌아온 뒤 초당 {속도[시간[1:] > 2.6].max():.0f}도")
    print(f"  마지막 wrist_roll {round(참들[-1, 4], 1) + 0.0}도")
    이름 = "감시견 켬" if 감시견 else "감시견 끔"
    칸들[0].plot(시간, 참들[:, 4], label=이름)
    칸들[1].plot(시간[1:], 속도, label=이름)
칸들[0].plot(시간, [목표_자세(t)[4] for t in 시간], color="gray", linestyle="--", label="궤적")
칸들[0].set_ylabel("wrist_roll 각도(도)")
칸들[1].set_ylabel("가장 빠른 관절 속도(도/초)")
for 칸 in 칸들:
    칸.axvspan(2.0, 2.6, color="tab:red", alpha=0.15)
    칸.set_xlabel("시간(초)")
    칸.legend(fontsize=8)
그림.tight_layout()
그림.savefig("so101_watchdog.png", dpi=200)
print("저장: so101_watchdog.png")
