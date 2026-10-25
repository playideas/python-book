"""12장: 모터 하나로 돌리는 진자. 각도 0은 똑바로 아래, 단위는 rad와 N·m."""
from collections.abc import Callable

import mujoco
import numpy as np

XML = """
<mujoco>
  <option timestep="0.001"/>
  <worldbody>
    <body pos="0 0 1">
      <joint name="pivot" type="hinge" axis="0 1 0" damping="0.02"/>
      <geom type="capsule" fromto="0 0 0 0 0 -0.5" size="0.01" mass="0.01"/>
      <geom type="sphere" pos="0 0 -0.5" size="0.04" mass="1"/>
    </body>
  </worldbody>
  <actuator><motor name="모터" joint="pivot" ctrlrange="-50 50"/></actuator>
</mujoco>
"""


def 실행(제어기: Callable, 목표: float | Callable[[float], float], 시간: float = 3.0,
       주기: float = 0.01, 잡음: float = 0.0, 토크_한계: float = 50.0,
       시드: int = 0) -> dict[str, np.ndarray]:
    """주기마다 각도를 재서 제어기(목표, 잰_각도)에 묻고, 받은 토크를 다음 주기까지 그대로 준다."""
    모델 = mujoco.MjModel.from_xml_string(XML)
    모델.actuator_ctrlrange[0] = [-토크_한계, 토크_한계]     # 모터가 낼 수 있는 토크의 범위
    데이터 = mujoco.MjData(모델)
    생성기 = np.random.default_rng(시드)
    한_주기_걸음 = round(주기 / 모델.opt.timestep)
    기록 = {"시각": [], "목표": [], "각도": [], "잰_각도": [], "요청": [], "토크": []}
    for k in range(round(시간 / 주기)):
        t = k * 주기
        목표값 = 목표(t) if callable(목표) else 목표
        각도 = 데이터.qpos[0]
        잰_각도 = 각도 + 생성기.normal(0, 잡음) if 잡음 > 0 else 각도
        요청 = 제어기(목표값, 잰_각도)
        데이터.ctrl[0] = 요청                  # 한계를 넘는 몫은 MuJoCo가 ctrlrange로 자른다
        실제 = float(np.clip(요청, -토크_한계, 토크_한계))
        for 이름, 값 in zip(기록, [t, 목표값, 각도, 잰_각도, 요청, 실제]):
            기록[이름].append(값)
        for _ in range(한_주기_걸음):
            mujoco.mj_step(모델, 데이터)
    return {이름: np.array(값) for 이름, 값 in 기록.items()}
