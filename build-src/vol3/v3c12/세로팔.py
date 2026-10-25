"""12장 실습: 세로로 선 평면 2관절 팔. 각도 0은 수평, 양수는 위로 드는 쪽."""
from collections.abc import Callable

import mujoco
import numpy as np

L1, L2 = 0.30, 0.25                      # 위팔·아래팔 길이(m), 4장 실습 팔과 같다
토크_한계 = np.array([20.0, 8.0])        # 어깨·팔꿈치 모터가 낼 수 있는 토크(N·m)


def 장면(짐: float = 0.0) -> str:
    """손끝에 짐(kg)을 든 팔의 MJCF. 받침 원통은 팔과 부딪히지 않게 충돌을 끈다."""
    return f"""
<mujoco model="세로 2관절 팔">
  <option timestep="0.001" integrator="implicitfast"/>
  <asset>
    <texture type="skybox" builtin="gradient" rgb1="0.95 0.95 1" rgb2="0.6 0.7 0.8" width="256" height="256"/>
  </asset>
  <default><joint type="hinge" axis="0 -1 0" damping="0.5"/></default>
  <worldbody>
    <light pos="0 -1.5 2" dir="0 0.6 -1"/>
    <camera name="side" pos="0.1 -1.6 0.75" xyaxes="1 0 0 0 0 1"/>
    <geom type="plane" size="1 1 0.1" rgba="0.85 0.85 0.85 1"/>
    <body name="base" pos="0 0 0.8">
      <geom type="cylinder" fromto="0 0.06 0 0 0.03 0" size="0.04" rgba="0.3 0.3 0.3 1"
            contype="0" conaffinity="0"/>
      <body name="upper">
        <joint name="shoulder"/>
        <geom type="capsule" fromto="0 0 0 {L1} 0 0" size="0.025" mass="1.0" rgba="0.2 0.5 0.9 1"/>
        <body name="lower" pos="{L1} 0 0">
          <joint name="elbow"/>
          <geom type="capsule" fromto="0 0 0 {L2} 0 0" size="0.02" mass="0.6" rgba="0.2 0.7 0.5 1"/>
          <geom type="sphere" pos="{L2} 0 0" size="0.035" mass="{0.4 + 짐}" rgba="0.9 0.3 0.2 1"/>
          <site name="tip" pos="{L2} 0 0"/>
        </body>
      </body>
    </body>
  </worldbody>
  <actuator>
    <motor name="shoulder" joint="shoulder" ctrlrange="-{토크_한계[0]} {토크_한계[0]}"/>
    <motor name="elbow" joint="elbow" ctrlrange="-{토크_한계[1]} {토크_한계[1]}"/>
  </actuator>
</mujoco>
"""


def 실행(제어기들: list[Callable], 목표: Callable[[float], np.ndarray], 시간: float,
       중력_보상: bool = False, 짐: float = 0.0, 주기: float = 0.01,
       시작: tuple[float, float] = (-np.pi / 2, 0.0)) -> dict[str, np.ndarray]:
    """관절마다 제어기(목표, 잰_각도, 앞먹임)를 하나씩 두고 주기마다 토크를 정한다.

    중력_보상이 참이면 짐을 모르는 팔 모델로 계산한 qfrc_bias를 앞먹임으로 더한다.
    """
    모델 = mujoco.MjModel.from_xml_string(장면(짐))            # 진짜 팔(짐을 들었을 수 있다)
    데이터 = mujoco.MjData(모델)
    아는_모델 = mujoco.MjModel.from_xml_string(장면())          # 제어기가 알고 있는 팔
    아는_데이터 = mujoco.MjData(아는_모델)
    데이터.qpos[:] = 시작
    mujoco.mj_forward(모델, 데이터)
    기록 = {"시각": [], "목표": [], "각도": [], "토크": [], "손끝": []}
    for k in range(round(시간 / 주기)):
        t = k * 주기
        목표값 = 목표(t)
        앞먹임 = np.zeros(2)
        if 중력_보상:
            아는_데이터.qpos[:], 아는_데이터.qvel[:] = 데이터.qpos, 데이터.qvel
            mujoco.mj_forward(아는_모델, 아는_데이터)
            앞먹임 = 아는_데이터.qfrc_bias.copy()
        토크 = [제어기(목표값[i], 데이터.qpos[i], 앞먹임[i]) for i, 제어기 in enumerate(제어기들)]
        데이터.ctrl[:] = 토크
        for 이름, 값 in zip(기록, [t, 목표값, 데이터.qpos.copy(), np.clip(토크, -토크_한계, 토크_한계),
                                 데이터.site("tip").xpos[[0, 2]].copy()]):
            기록[이름].append(값)
        for _ in range(round(주기 / 모델.opt.timestep)):
            mujoco.mj_step(모델, 데이터)
        mujoco.mj_forward(모델, 데이터)         # 손끝 위치를 걸음을 마친 상태로 맞춘다
    return {이름: np.array(값) for 이름, 값 in 기록.items()}
