import matplotlib.pyplot as plt
import numpy as np

from 세로팔 import 실행, 토크_한계
from 실전PID import 실전PID

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

목표들 = np.deg2rad([[-30, 60], [20, 40], [45, -45], [-60, 30]])    # (어깨, 팔꿈치)
머무름, 주기 = 2.0, 0.01


def 목표(t: float) -> np.ndarray:
    return 목표들[min(int(t // 머무름), len(목표들) - 1)]


def 제어기들(ki_배율: float, kd_배율: float, 분리: float = np.inf) -> list[실전PID]:
    """어깨(kp 40)와 팔꿈치(kp 15)의 PID. 배율로 I, D를 켜고 끈다."""
    return [실전PID(40, 40 * ki_배율, 4 * kd_배율, 주기, 출력_한계=토크_한계[0], 적분_구간=분리),
            실전PID(15, 15 * ki_배율, 1 * kd_배율, 주기, 출력_한계=토크_한계[1], 적분_구간=분리)]


def 성적(기록: dict) -> tuple[float, float, float]:
    """목표마다 두 관절이 모두 ±2도 안에 들어와 머문 시각과, 머무름이 끝날 때의 오차."""
    오차_도 = np.rad2deg(np.abs(기록["목표"] - 기록["각도"]))
    n = round(머무름 / 주기)
    도착들, 끝_오차 = [], []
    for 구간 in range(len(목표들)):
        조각 = 오차_도[구간 * n:(구간 + 1) * n]
        밖 = 조각.max(axis=1) > 2.0
        도착들.append(np.nan if 밖[-1] else (np.flatnonzero(밖)[-1] + 1) * 주기 if 밖.any() else 0.0)
        끝_오차.append(조각[-1])
    끝 = np.mean(끝_오차, axis=0)
    return np.nanmean(도착들) if not np.isnan(도착들).all() else np.nan, int(np.isnan(도착들).sum()), 끝


경우들 = {"P만": (dict(ki_배율=0, kd_배율=0), False),
        "PID": (dict(ki_배율=1, kd_배율=1), False),
        "PID + 중력 보상": (dict(ki_배율=1, kd_배율=1), True),
        "PID + 중력 보상 + 적분 분리": (dict(ki_배율=1, kd_배율=1, 분리=np.deg2rad(5)), True)}
그림, 칸들 = plt.subplots(2, 1, figsize=(8, 5), sharex=True)
print("제어기                    | 짐   | 평균 도착 | 못 감 | 끝 오차(어깨, 팔꿈치)")
for 이름, (설정, 보상) in 경우들.items():
    for 짐 in [0.0, 0.5]:
        기록 = 실행(제어기들(**설정), 목표, 시간=머무름 * len(목표들), 중력_보상=보상, 짐=짐)
        평균_도착, 못_감, 끝 = 성적(기록)
        도착_글 = "  -  " if np.isnan(평균_도착) else f"{평균_도착:.2f}초"
        print(f"{이름:22s} | {짐:.1f}kg | {도착_글:>8s} | {못_감}/4 | {끝[0]:5.2f}도, {끝[1]:5.2f}도")
        if 짐 == 0.0:
            for j in range(2):
                칸들[j].plot(기록["시각"], np.rad2deg(기록["각도"][:, j]), linewidth=1.2, label=이름)
for j, 관절 in enumerate(["어깨", "팔꿈치"]):
    칸들[j].plot(기록["시각"], np.rad2deg(기록["목표"][:, j]), color="black", linestyle="--",
               linewidth=1, label="목표")
    칸들[j].set_ylabel(f"{관절} 각도(도)")
칸들[0].set_ylim(-150, 70)
칸들[0].legend(fontsize=7, ncol=3, loc="lower left")
칸들[1].set_xlabel("시간(초)")
그림.tight_layout()
그림.savefig("arm_pid_compare.png", dpi=200)
print("저장: arm_pid_compare.png")
