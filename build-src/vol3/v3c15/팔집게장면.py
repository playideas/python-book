"""15장: 3장의 6자유도 예제 팔 끝에 평행 집게를 달고 탁자 위에 놓는다."""
import mujoco
import numpy as np

from 집게 import TCP, 손가락_최대, 집게_몸체, 집게_부속
from 팔도구 import 변환, 예제_팔

받침_위치 = np.array([0.0, 0.0, 0.4])       # 팔 받침은 탁자 윗면(높이 0.4m)에 붙어 있다
T_세계_받침 = 변환(np.eye(3), 받침_위치)
손끝_집게 = [0, 0, 0.05 + TCP]              # 마지막 관절 기준 TCP: 손바닥(0.05) + 손가락 쪽(TCP)
상자_반크기 = np.array([0.04, 0.025, 0.025])  # 길이 8cm, 너비 5cm, 높이 5cm
집_자세 = np.deg2rad([0, 30, 90, 0, 60, 0])    # 출발 자세: 손가락이 바로 아래를 본다


def 글(벡터) -> str:
    return " ".join(f"{float(값):.6g}" for 값 in 벡터)


def 장면_xml(상자_위치=(0.4, 0.1), 상자_요_도: float = 0.0, 놓을_곳=(0.3, -0.25),
            쥐는_힘: float = 10.0, 상자_질량: float = 0.1) -> str:
    """팔·집게·상자·놓을 곳 표시가 든 MJCF. 상자 위치는 탁자 위 (x, y)(m)."""
    몸체들 = []
    for i, (_, 위치, 축) in enumerate(예제_팔):
        다음 = 예제_팔[i + 1][1] if i + 1 < len(예제_팔) else [0, 0, 0.03]
        몸체들.append(f'<body name="link{i + 1}" pos="{글(위치)}" gravcomp="1">'
                    f'<joint name="joint{i + 1}" axis="{글(축)}"/>'
                    f'<geom type="capsule" fromto="0 0 0 {글(다음)}" size="0.02" rgba="0.8 0.5 0.2 1"/>')
    상자_z = 받침_위치[2] + 상자_반크기[2]
    return f"""
<mujoco model="집게 단 6자유도 팔">
  <option timestep="0.002" integrator="implicitfast" cone="elliptic" impratio="10"/>
  <asset>
    <texture type="skybox" builtin="gradient" rgb1="0.95 0.95 1" rgb2="0.6 0.7 0.8" width="256" height="256"/>
    <texture name="격자" type="2d" builtin="checker" rgb1="0.25 0.3 0.35" rgb2="0.75 0.75 0.75"
             width="256" height="256"/>
    <material name="바닥재" texture="격자" texrepeat="8 8"/>
  </asset>
  <default>
    <joint type="hinge" damping="1" armature="0.05"/>
    <geom contype="2" conaffinity="1"/>
    <position kp="400" dampratio="1"/>
  </default>
  <worldbody>
    <light pos="0.3 -0.5 2.5" dir="0 0.2 -1"/>
    <camera name="top" pos="0.4 0 1.2" xyaxes="1 0 0 0 1 0" fovy="50"/>
    <geom name="floor" type="plane" size="2 2 0.1" material="바닥재" contype="1"/>
    <geom name="table" type="box" pos="0.35 0 0.2" size="0.45 0.5 0.2" rgba="0.75 0.6 0.45 1"
          contype="1" friction="0.5 0.005 0.0001"/>
    <geom name="target" type="cylinder" pos="{글(놓을_곳)} 0.4005" size="0.05 0.0005"
          rgba="0.2 0.7 0.3 0.6" contype="0" conaffinity="0"/>
    <body name="base" pos="{글(받침_위치)}">
      <geom type="cylinder" fromto="0 0 0 0 0 0.1" size="0.05" rgba="0.3 0.3 0.3 1"/>
      {"".join(몸체들)}{집게_몸체("0 0 0.05")}{"</body>" * len(예제_팔)}
    </body>
    <body name="box" pos="{글(상자_위치)} {상자_z}" euler="0 0 {상자_요_도}">
      <freejoint/>
      <geom name="box" type="box" size="{글(상자_반크기)}" mass="{상자_질량}" contype="1"
            friction="0.5 0.005 0.0001" rgba="0.95 0.75 0.1 1"/>
    </body>
  </worldbody>
  <actuator>
    {"".join(f'<position name="joint{i + 1}" joint="joint{i + 1}"/>' for i in range(len(예제_팔)))}
  </actuator>
  {집게_부속(쥐는_힘)}
</mujoco>"""


def 준비(모델: mujoco.MjModel, 데이터: mujoco.MjData) -> None:
    """팔을 출발 자세에 두고 손가락을 활짝 연다(관절 값과 명령을 함께)."""
    데이터.qpos[:6] = 데이터.ctrl[:6] = 집_자세
    데이터.joint("finger_l").qpos = 데이터.joint("finger_r").qpos = 손가락_최대
    데이터.ctrl[모델.actuator("grip").id] = 2 * 손가락_최대
    mujoco.mj_forward(모델, 데이터)
