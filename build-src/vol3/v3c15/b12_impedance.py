import matplotlib.pyplot as plt
import mujoco
import numpy as np

from 집게시험장면 import 들기, 만들기, 흘려보내기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
질량 = 0.2


def 탁자_힘(모델, 데이터) -> float:
    """상자와 탁자 사이 접촉의 수직력 합(N). 4장 4.8절의 mj_contactForce."""
    짝, 힘, 합 = {모델.geom("box").id, 모델.geom("table").id}, np.zeros(6), 0.0
    for i, c in enumerate(데이터.contact[:데이터.ncon]):
        if {c.geom1, c.geom2} == 짝:
            mujoco.mj_contactForce(모델, 데이터, i, 힘)
            합 += 힘[0]
    return 합


def 내려놓기(kp: float, 멈추기: bool) -> tuple[list[float], list[float]]:
    """6cm 위에서 '탁자보다 1cm 아래'를 목표로 1초 동안 내려놓는다. 멈추기면 닿는 순간 그 자리에 선다."""
    모델, 데이터 = 만들기(쥐는_힘=30.0, 상자_질량=질량, 들기_kp=kp)   # 상자가 손가락 사이에서 밀리지 않게 세게
    영점 = 데이터.sensor("wrist_force").data[2]
    데이터.ctrl[모델.actuator("grip").id] = 0.0
    흘려보내기(모델, 데이터, 0.5)
    들기(모델, 데이터, 0.06)
    들기_번호, 시작, 시각, 힘들 = 모델.actuator("lift").id, 데이터.time, [], []
    섰다 = False
    while 데이터.time < 시작 + 1.5:
        s = min((데이터.time - 시작) / 1.0, 1.0)
        하중 = 영점 - 데이터.sensor("wrist_force").data[2]                # 집게가 떠받치는 상자 무게(N)
        if 멈추기 and not 섰다 and s > 0.1 and 하중 < 0.5 * 질량 * 9.81:   # 무게 절반이 탁자로 넘어갔다
            데이터.ctrl[들기_번호] = 데이터.qpos[모델.joint("lift").qposadr[0]]
            섰다 = True
        if not 섰다:
            데이터.ctrl[들기_번호] = 0.06 + (-0.01 - 0.06) * (3 * s**2 - 2 * s**3)
        mujoco.mj_step(모델, 데이터)
        시각.append(데이터.time - 시작)
        힘들.append(탁자_힘(모델, 데이터))
    return 시각, 힘들


그림, 칸 = plt.subplots(figsize=(7, 3.4))
for kp, 멈추기 in [(1000, False), (500, False), (200, False), (1000, True)]:
    시각, 힘들 = 내려놓기(kp, 멈추기)
    이름 = f"kp={kp}" + (", 닿으면 멈춤" if 멈추기 else "")
    print(f"{이름:16s}: 가장 큰 힘 {max(힘들):6.2f}N, 마지막 {힘들[-1]:6.2f}N "
          f"(상자 무게 {질량 * 9.81:.2f}N + kp × 1cm = {질량 * 9.81 + kp * 0.01 * (not 멈추기):6.2f}N)")
    칸.plot(시각, 힘들, label=이름, linestyle="--" if 멈추기 else "-")
칸.set_xlabel("내려놓기 시작 뒤 시간(초)")
칸.set_ylabel("탁자가 받치는 힘(N)")
칸.legend(fontsize=8)
그림.tight_layout()
그림.savefig("impedance.png", dpi=200)
print("저장: impedance.png")
