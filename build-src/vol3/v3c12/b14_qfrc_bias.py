import mujoco
import numpy as np

from 진자장면 import XML

모델 = mujoco.MjModel.from_xml_string(XML)
데이터 = mujoco.MjData(모델)
for 각도_도 in [0, 30, 60, 90, 150]:
    데이터.qpos[0], 데이터.qvel[0] = np.deg2rad(각도_도), 0.0
    mujoco.mj_forward(모델, 데이터)                            # 지금 자세에서 힘들을 계산만 한다
    식 = 9.81 * (1.0 * 0.5 + 0.01 * 0.25) * np.sin(np.deg2rad(각도_도))   # 들어가며의 중력_토크
    print(f"{각도_도:3d}도: qfrc_bias {데이터.qfrc_bias[0]:6.3f}N·m, 식 {식:6.3f}N·m")

# qfrc_bias만큼 모터로 밀어 주면 진자는 그 자리에 떠 있을까?
데이터.qpos[0], 데이터.qvel[0] = np.deg2rad(60), 0.0
for _ in range(2000):                                         # 2초
    mujoco.mj_forward(모델, 데이터)
    데이터.ctrl[0] = 데이터.qfrc_bias[0]
    mujoco.mj_step(모델, 데이터)
print(f"2초 동안 qfrc_bias만 줬을 때 각도: {np.rad2deg(데이터.qpos[0]):.4f}도")
