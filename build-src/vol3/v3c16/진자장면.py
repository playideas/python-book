"""16장: 4장의 진자(0.5m 막대 끝에 1kg 추)에 힘이 약한 모터를 단 장면. 각도 0은 매달린 자세, ±π가 거꾸로 선 자세."""
import mujoco
import numpy as np

토크_한계 = 2.0                     # N·m. 추를 옆으로 들어 버티는 데만 약 4.9N·m가 필요하다
xml = f"""
<mujoco>
  <option timestep="0.01"/>
  <worldbody>
    <light pos="0 -1 3" dir="0 0.3 -1"/>
    <camera name="옆" pos="0 -1.7 1" xyaxes="1 0 0 0 0 1"/>
    <geom type="plane" pos="0 0.15 1" zaxis="0 -1 0" size="1 1 0.1" rgba="0.9 0.9 0.88 1" contype="0" conaffinity="0"/>
    <geom type="box" pos="0 0.05 1" size="0.04 0.02 0.04" rgba="0.3 0.3 0.3 1" contype="0" conaffinity="0"/>
    <body pos="0 0 1">
      <joint name="축" type="hinge" axis="0 1 0" damping="0.05"/>
      <geom type="capsule" fromto="0 0 0 0 0 -0.5" size="0.01" mass="0.01"/>
      <geom type="sphere" pos="0 0 -0.5" size="0.04" mass="1" rgba="0.9 0.4 0.1 1"/>
    </body>
  </worldbody>
  <actuator><motor joint="축" ctrlrange="-{토크_한계} {토크_한계}"/></actuator>
</mujoco>
"""


def 장면() -> tuple[mujoco.MjModel, mujoco.MjData]:
    모델 = mujoco.MjModel.from_xml_string(xml)
    return 모델, mujoco.MjData(모델)


def 세운_자세_오차(각도: np.ndarray) -> np.ndarray:
    """거꾸로 선 자세(π)에서 벗어난 각도를 -π~π로 감싸서 돌려준다(rad)."""
    return (각도 - np.pi + np.pi) % (2 * np.pi) - np.pi
