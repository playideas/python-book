import mujoco
import numpy as np

from 진자장면 import 장면

모델, 진짜 = 장면()
상태_종류 = mujoco.mjtState.mjSTATE_FULLPHYSICS          # 시각 + qpos + qvel (+ 있으면 액추에이터 상태 등)
print("상태 크기:", mujoco.mj_stateSize(모델, 상태_종류), "= 시각 1 + qpos", 모델.nq, "+ qvel", 모델.nv)

# 진짜 진자를 1초 동안 흔든다
for k in range(100):
    진짜.ctrl[0] = 2.0 * np.sign(np.sin(k * 0.1))
    mujoco.mj_step(모델, 진짜)

# 지금 상태를 복사해 '상상용' 데이터에 넣는다. 진짜는 건드리지 않는다
지금 = np.empty(mujoco.mj_stateSize(모델, 상태_종류))
mujoco.mj_getState(모델, 진짜, 지금, 상태_종류)
상상 = mujoco.MjData(모델)
mujoco.mj_setState(모델, 상상, 지금, 상태_종류)

계획 = np.full(50, -1.5)                                 # 앞으로 0.5초 동안 -1.5N·m를 줘 볼까?
for u in 계획:
    상상.ctrl[0] = u
    mujoco.mj_step(모델, 상상)
print(f"상상: 0.5초 뒤 각도 {상상.qpos[0]:.4f}rad (시각 {상상.time:.2f}초)")
print(f"진짜는 그대로: 각도 {진짜.qpos[0]:.4f}rad (시각 {진짜.time:.2f}초)")

# 그 계획을 진짜로 실행하면?
for u in 계획:
    진짜.ctrl[0] = u
    mujoco.mj_step(모델, 진짜)
print(f"진짜로 해 보니: 0.5초 뒤 각도 {진짜.qpos[0]:.4f}rad, 상상과 차이 {abs(진짜.qpos[0] - 상상.qpos[0])}")
