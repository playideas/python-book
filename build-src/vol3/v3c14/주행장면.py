"""14장: 11장과 비슷한 방에 바퀴 둘 달린 로봇을 들여놓은 MuJoCo 장면과 2차원 라이다."""
import mujoco
import numpy as np

from 이동도구 import 바퀴_간격, 바퀴_반지름

# group="1"인 물체는 지도를 만든 뒤에 생긴 것이라 지도에 없다(지나가는 사람, 누가 놓고 간 상자)
방_XML = f"""
<mujoco>
  <option timestep="0.002" integrator="implicitfast"/>
  <visual><headlight ambient="0.3 0.3 0.3" diffuse="0.3 0.3 0.3" specular="0 0 0"/></visual>
  <default><geom rgba="0.55 0.57 0.62 1"/></default>
  <worldbody>
    <light pos="5 4 10" dir="0 0 -1" directional="true" diffuse="0.45 0.45 0.45" specular="0 0 0"/>
    <geom type="plane" pos="5 4 0" size="5.6 4.6 0.1" rgba="0.92 0.92 0.88 1"/>
    <geom type="box" pos="5 -0.1 0.5" size="5.2 0.1 0.5"/>
    <geom type="box" pos="5 8.1 0.5" size="5.2 0.1 0.5"/>
    <geom type="box" pos="-0.1 4 0.5" size="0.1 4 0.5"/>
    <geom type="box" pos="10.1 4 0.5" size="0.1 4 0.5"/>
    <geom type="box" pos="5 4 0.5" size="2 1 0.5" rgba="0.45 0.5 0.6 1"/>
    <geom type="box" pos="1.1 4 0.5" size="1.1 0.05 0.5"/>
    <geom type="cylinder" pos="0.7 0.7 0.5" size="0.25 0.5" rgba="0.8 0.45 0.3 1"/>
    <geom type="cylinder" pos="5 0.6 0.5" size="0.2 0.5" rgba="0.8 0.45 0.3 1"/>
    <geom type="cylinder" pos="9.2 6.2 0.5" size="0.3 0.5" rgba="0.8 0.45 0.3 1"/>
    <geom type="box" pos="2.6 7.6 0.4" size="0.6 0.3 0.4" rgba="0.6 0.5 0.35 1"/>
    <geom type="box" pos="8.9 0.5 0.4" size="0.4 0.4 0.4" rgba="0.6 0.5 0.35 1"/>
    <geom type="box" pos="7.4 7.7 0.4" size="0.3 0.2 0.4" rgba="0.6 0.5 0.35 1"/>
    <geom name="상자" type="box" pos="8.5 4 0.3" size="1.5 0.25 0.3" group="1" rgba="0.85 0.2 0.2 1"/>
    <body name="사람" mocap="true" pos="5.6 2 0">
      <geom type="cylinder" size="0.2 0.8" pos="0 0 0.8" group="1" rgba="0.3 0.4 0.9 1"/>
    </body>
    <body name="로봇" pos="1.5 1.5 0.05">
      <freejoint/>
      <geom type="cylinder" size="0.18 0.03" pos="0 0 0.03" mass="2" rgba="0.2 0.6 0.3 1"/>
      <geom type="box" size="0.05 0.03 0.02" pos="0.12 0 0.08" mass="0.01" rgba="0.95 0.95 0.95 1"/>
      <geom type="sphere" size="0.02" pos="0.13 0 -0.026" condim="1" mass="0.02"/>
      <geom type="sphere" size="0.02" pos="-0.13 0 -0.026" condim="1" mass="0.02"/>
      <body name="왼바퀴" pos="0 {바퀴_간격 / 2} 0">
        <joint name="왼쪽" type="hinge" axis="0 1 0" armature="0.001"/>
        <geom type="cylinder" size="{바퀴_반지름} 0.01" euler="90 0 0" mass="0.2" rgba="0.2 0.2 0.2 1"/>
      </body>
      <body name="오른바퀴" pos="0 {-바퀴_간격 / 2} 0">
        <joint name="오른쪽" type="hinge" axis="0 1 0" armature="0.001"/>
        <geom type="cylinder" size="{바퀴_반지름} 0.01" euler="90 0 0" mass="0.2" rgba="0.2 0.2 0.2 1"/>
      </body>
    </body>
  </worldbody>
  <actuator>
    <velocity name="왼쪽" joint="왼쪽" kv="2" ctrlrange="-12 12" forcerange="-3 3"/>
    <velocity name="오른쪽" joint="오른쪽" kv="2" ctrlrange="-12 12" forcerange="-3 3"/>
  </actuator>
</mujoco>
"""

라이다_높이 = 0.3     # m. 로봇 몸(높이 0.11m)보다 높게 쏜다
라이다_최대 = 6.0     # m


def 장면_만들기(로봇_포즈=(1.5, 1.5, 0.0), 더할_XML: str = "") -> tuple[mujoco.MjModel, mujoco.MjData]:
    """더할_XML: 지도에 없는 물체를 더 놓을 때(group="1"로)."""
    모델 = mujoco.MjModel.from_xml_string(방_XML.replace("</worldbody>", 더할_XML + "</worldbody>"))
    데이터 = mujoco.MjData(모델)
    x, y, θ = 로봇_포즈
    데이터.qpos[:7] = [x, y, 0.05, np.cos(θ / 2), 0, 0, np.sin(θ / 2)]
    mujoco.mj_forward(모델, 데이터)
    return 모델, 데이터


def 로봇_포즈(데이터: mujoco.MjData) -> np.ndarray:
    """MuJoCo가 아는 참 포즈 (x, y, θ)."""
    w, x, y, z = 데이터.qpos[3:7]
    return np.array([데이터.qpos[0], 데이터.qpos[1], np.arctan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))])


def 라이다(모델: mujoco.MjModel, 데이터: mujoco.MjData, 개수: int = 120) -> np.ndarray:
    """로봇 둘레를 한 바퀴 재서 맞은 곳을 방 기준 점들(N×2)로 돌려준다."""
    x, y, θ = 로봇_포즈(데이터)
    각도들 = θ + np.arange(개수) * 2 * np.pi / 개수
    방향들 = np.stack([np.cos(각도들), np.sin(각도들), np.zeros(개수)], axis=1)
    거리 = np.zeros(개수)
    맞은_것 = np.zeros(개수, dtype=np.int32)
    mujoco.mj_multiRay(모델, 데이터, np.array([x, y, 라이다_높이]), 방향들.ravel(), None, True,
                       모델.body("로봇").id, 맞은_것, 거리, None, 개수, 라이다_최대)
    맞음 = (거리 > 0) & (거리 <= 라이다_최대)
    return np.column_stack([x + 거리[맞음] * np.cos(각도들[맞음]), y + 거리[맞음] * np.sin(각도들[맞음])])
