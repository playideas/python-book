import matplotlib.pyplot as plt
import mujoco
import numpy as np

from 진자장면 import XML, 실행
from 피아이디 import PID

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# 진자의 관성 모멘트 J를 MuJoCo에게 묻는다(관절 공간의 질량 행렬, 여기서는 1×1)
모델 = mujoco.MjModel.from_xml_string(XML)
데이터 = mujoco.MjData(모델)
mujoco.mj_forward(모델, 데이터)
질량_행렬 = np.zeros((1, 1))
mujoco.mj_fullM(모델, 데이터, 질량_행렬)
J = 질량_행렬[0, 0]
kp = 30
중력_용수철 = 9.81 * 0.5025 * np.cos(np.deg2rad(60))      # 60도 근처에서 중력이 더하는 용수철 효과
임계_kd = 2 * np.sqrt(J * (kp + 중력_용수철))
print(f"J = {J:.4f} kg·m², 흔들림이 딱 사라지는 kd ≈ {임계_kd:.2f}")

목표 = np.deg2rad(60)
그림, 칸 = plt.subplots(figsize=(7, 3.4))
for kd in [0, 1, 3, round(임계_kd, 1), 12]:
    기록 = 실행(PID(kp, 0, kd, 주기=0.01), 목표, 시간=3.0)
    각도_도 = np.rad2deg(기록["각도"])
    멈춘 = 각도_도[-50:].mean()                              # 마지막 0.5초의 평균
    밖 = np.abs(각도_도 - 멈춘) > 1.0
    자리_잡음 = f"{기록['시각'][np.flatnonzero(밖)[-1] + 1]:.2f}초" if not 밖[-1] else "  못 함"
    print(f"kd={kd:4.1f}: 가장 높이 {각도_도.max():5.1f}도, 끝 {멈춘:5.1f}도, 끝 ±1도 안에 자리 잡음 {자리_잡음}")
    칸.plot(기록["시각"], 각도_도, label=f"kd={kd}")
칸.axhline(60, color="gray", linestyle="--", linewidth=1)
칸.set_xlabel("시간(초)")
칸.set_ylabel("각도(도)")
칸.set_ylim(-60, 160)
칸.legend(fontsize=8, ncol=5, loc="upper center")
그림.tight_layout()
그림.savefig("add_d.png", dpi=200)
print("저장: add_d.png")
