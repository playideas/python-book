import matplotlib.pyplot as plt
import mujoco
import numpy as np

from 실전PID import 실전PID
from 진자장면 import XML

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

목표 = np.deg2rad(120)
최대_속도 = 2.0                           # 바깥 고리가 내줄 수 있는 가장 빠른 속도(rad/s)


def 계단식(시간: float = 3.0) -> dict[str, np.ndarray]:
    """바깥: 50Hz 위치 P → 목표 속도. 안쪽: 500Hz 속도 PI → 토크."""
    모델 = mujoco.MjModel.from_xml_string(XML)
    데이터 = mujoco.MjData(모델)
    속도_제어기 = 실전PID(10.0, 200.0, 0.0, 주기=0.002, 출력_한계=50.0)
    기록 = {"시각": [], "각도": [], "속도": [], "목표_속도": []}
    for k in range(round(시간 / 0.002)):
        if k % 10 == 0:                                    # 0.02초마다 바깥 고리
            목표_속도 = np.clip(5.0 * (목표 - 데이터.qpos[0]), -최대_속도, 최대_속도)
        데이터.ctrl[0] = 속도_제어기(목표_속도, 데이터.qvel[0])   # 0.002초마다 안쪽 고리
        for 이름, 값 in zip(기록, [k * 0.002, 데이터.qpos[0], 데이터.qvel[0], 목표_속도]):
            기록[이름].append(값)
        for _ in range(2):
            mujoco.mj_step(모델, 데이터)
    return {이름: np.array(값) for 이름, 값 in 기록.items()}


def 한_고리(시간: float = 3.0) -> dict[str, np.ndarray]:
    """비교: 100Hz 위치 PID 하나로 토크를 바로 정한다."""
    모델 = mujoco.MjModel.from_xml_string(XML)
    데이터 = mujoco.MjData(모델)
    제어기 = 실전PID(30, 30, 5.7, 주기=0.01, 출력_한계=50.0)
    기록 = {"시각": [], "각도": [], "속도": []}
    for k in range(round(시간 / 0.01)):
        데이터.ctrl[0] = 제어기(목표, 데이터.qpos[0])
        for 이름, 값 in zip(기록, [k * 0.01, 데이터.qpos[0], 데이터.qvel[0]]):
            기록[이름].append(값)
        for _ in range(10):
            mujoco.mj_step(모델, 데이터)
    return {이름: np.array(값) for 이름, 값 in 기록.items()}


그림, (위, 아래) = plt.subplots(2, 1, figsize=(7, 4.6), sharex=True)
for 이름, 기록 in [("PID 하나", 한_고리()), ("계단식(위치 P → 속도 PI)", 계단식())]:
    각도_도 = np.rad2deg(기록["각도"])
    print(f"{이름}: 가장 빠를 때 {np.abs(기록['속도']).max():.2f}rad/s, 가장 높이 {각도_도.max():6.2f}도, "
          f"끝 {각도_도[-1]:6.2f}도")
    위.plot(기록["시각"], 각도_도, label=이름)
    아래.plot(기록["시각"], 기록["속도"], label=이름)
아래.plot(기록["시각"], 기록["목표_속도"], color="gray", linestyle="--", linewidth=1, label="바깥 고리가 준 목표 속도")
위.axhline(120, color="gray", linestyle="--", linewidth=1)
위.set_ylabel("각도(도)")
위.legend(fontsize=8, loc="lower right")
아래.set_ylabel("각속도(rad/s)")
아래.set_xlabel("시간(초)")
아래.legend(fontsize=8, loc="upper right")
그림.tight_layout()
그림.savefig("cascade.png", dpi=200)
print("저장: cascade.png")
