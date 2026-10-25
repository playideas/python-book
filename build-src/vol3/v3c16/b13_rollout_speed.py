import os
import time

import mujoco
import numpy as np
from mujoco import rollout

from 진자장면 import 장면

모델, 데이터 = 장면()
상태_종류 = mujoco.mjtState.mjSTATE_FULLPHYSICS
지금 = np.empty(mujoco.mj_stateSize(모델, 상태_종류))
mujoco.mj_getState(모델, 데이터, 지금, 상태_종류)
K, T = 256, 100                                          # 후보 256개 × 1초(100걸음)
후보들 = np.random.default_rng(0).normal(0, 1, size=(K, T, 모델.nu))

# 1) 파이썬 for 문으로 하나씩 굴리기
시작 = time.perf_counter()
상상 = mujoco.MjData(모델)
각도1 = np.empty((K, T))
for i in range(K):
    mujoco.mj_setState(모델, 상상, 지금, 상태_종류)
    for t in range(T):
        상상.ctrl[:] = 후보들[i, t]
        mujoco.mj_step(모델, 상상)
        각도1[i, t] = 상상.qpos[0]
print(f"파이썬 for 문: {(time.perf_counter() - 시작) * 1000:5.1f}ms")

# 2) rollout 모듈: 반복을 C 안에서 돈다. MjData를 여러 개 주면 그 수만큼 스레드로 나눈다
for 스레드 in [1, 8]:
    상상들 = [mujoco.MjData(모델) for _ in range(스레드)]
    rollout.rollout(모델, 상상들, 지금, 후보들)           # 스레드를 준비하는 첫 호출은 빼고 잰다
    시작 = time.perf_counter()
    상태들, _ = rollout.rollout(모델, 상상들, 지금, 후보들)
    print(f"rollout, MjData {스레드}개: {(time.perf_counter() - 시작) * 1000:5.1f}ms "
          f"(결과 모양 {상태들.shape}, for 문과 같은가? {np.array_equal(상태들[:, :, 1], 각도1)})")
print("이 맥의 CPU 코어 수:", os.cpu_count())
