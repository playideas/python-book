import mujoco
import numpy as np

from 진자장면 import 세운_자세_오차, 장면, 토크_한계

모델, 데이터 = 장면()
kp, kd = 20.0, 2.0
각도들 = []
for _ in range(1000):                                    # 10초
    오차 = 세운_자세_오차(데이터.qpos[0])                     # 거꾸로 선 자세에서 얼마나 벗어났나
    토크 = -kp * 오차 - kd * 데이터.qvel[0]                   # 12장의 PD 제어: 위쪽으로 곧장 당긴다
    데이터.ctrl[0] = np.clip(토크, -토크_한계, 토크_한계)
    mujoco.mj_step(모델, 데이터)
    각도들.append(np.rad2deg(데이터.qpos[0]))
각도들 = np.array(각도들)
print(f"PD로 곧장 들어 올리기: 가장 높이 {각도들.max():.1f}도, "
      f"마지막 2초 동안 {각도들[-200:].min():.1f}~{각도들[-200:].max():.1f}도 (거꾸로 서려면 180도)")
print(f"모터 한계 {토크_한계}N·m로 버틸 수 있는 기울기: "
      f"{np.rad2deg(np.arcsin(토크_한계 / (1.0 * 9.81 * 0.5))):.1f}도 근처")
