"""13장 실습: 기둥 세 개가 선 탁자 위의 평면 3관절 팔. 4장 4.10절 팔장면을 한 마디 늘린 것."""
import mujoco
import numpy as np

길이들 = (0.30, 0.25, 0.15)          # 링크 길이(m)
팔_높이 = 0.45                       # 팔이 움직이는 평면의 높이(탁자 윗면 0.4m보다 5cm 위)
기둥들 = [(0.40, 0.12, 0.045),        # (x, y, 반지름) m. 받침 기준
          (0.12, 0.40, 0.045),
          (0.42, -0.24, 0.045)]
관절_한계 = np.deg2rad([[-170, 170], [-150, 150], [-150, 150]])
시작_자세 = np.deg2rad([-70.0, 25.0, 35.0])
목표_자세 = np.deg2rad([100.0, -115.0, 45.0])


def XML(kp: float = 50) -> str:
    L1, L2, L3 = 길이들
    기둥_글 = "".join(
        f'<geom name="pillar{i}" type="cylinder" pos="{x} {y} 0.5" size="{r} 0.1" rgba="0.8 0.45 0.3 1"/>'
        for i, (x, y, r) in enumerate(기둥들))
    범위 = [" ".join(f"{v:.0f}" for v in np.rad2deg(한계)) for 한계 in 관절_한계]   # MJCF 각도는 기본이 도
    return f"""
<mujoco model="기둥 사이의 3관절 팔">
  <option timestep="0.002" integrator="implicitfast"/>
  <asset>
    <texture type="skybox" builtin="gradient" rgb1="0.95 0.95 1" rgb2="0.6 0.7 0.8" width="256" height="256"/>
    <texture name="격자" type="2d" builtin="checker" rgb1="0.25 0.3 0.35" rgb2="0.75 0.75 0.75"
             width="256" height="256"/>
    <material name="바닥재" texture="격자" texrepeat="8 8"/>
  </asset>
  <default>
    <joint type="hinge" axis="0 0 1" damping="0.05" limited="true"/>
    <position kp="{kp}" dampratio="1"/>
  </default>
  <worldbody>
    <light pos="0.3 -0.5 2.5" dir="0 0.2 -1"/>
    <camera name="top" pos="0.1 0 2.1" xyaxes="1 0 0 0 1 0"/>
    <camera name="overview" pos="1.0 -0.9 1.15" xyaxes="0.67 0.74 0 -0.37 0.34 0.87"/>
    <geom name="floor" type="plane" size="2 2 0.1" material="바닥재"/>
    <geom name="table" type="box" pos="0.15 0 0.2" size="0.55 0.55 0.2" rgba="0.75 0.6 0.45 1"/>
    {기둥_글}
    <body name="base" pos="0 0 {팔_높이}">
      <geom type="cylinder" pos="0 0 -0.025" size="0.04 0.025" rgba="0.3 0.3 0.3 1" contype="0" conaffinity="0"/>
      <body name="link1">
        <joint name="j1" range="{범위[0]}"/>
        <geom name="arm1" type="capsule" fromto="0 0 0 {L1} 0 0" size="0.02" mass="0.3" rgba="0.2 0.5 0.9 1"/>
        <body name="link2" pos="{L1} 0 0">
          <joint name="j2" range="{범위[1]}"/>
          <geom name="arm2" type="capsule" fromto="0 0 0 {L2} 0 0" size="0.018" mass="0.2" rgba="0.2 0.7 0.5 1"/>
          <body name="link3" pos="{L2} 0 0">
            <joint name="j3" range="{범위[2]}"/>
            <geom name="arm3" type="capsule" fromto="0 0 0 {L3} 0 0" size="0.016" mass="0.1" rgba="0.9 0.6 0.2 1"/>
            <site name="tip" pos="{L3} 0 0" size="0.012" rgba="1 0.2 0.2 1"/>
          </body>
        </body>
      </body>
    </body>
  </worldbody>
  <actuator>
    <position joint="j1"/><position joint="j2"/><position joint="j3"/>
  </actuator>
</mujoco>
"""


class 충돌검사기:
    """MuJoCo에게 거리를 물어 자세가 안전한지 본다. 여유보다 가까우면 부딪힌 것으로 친다."""

    def __init__(self, 여유: float = 0.03) -> None:
        self.모델 = mujoco.MjModel.from_xml_string(XML())
        self.데이터 = mujoco.MjData(self.모델)
        self.여유 = 여유
        팔 = [self.모델.geom(f"arm{i}").id for i in (1, 2, 3)]
        기둥 = [self.모델.geom(f"pillar{i}").id for i in range(len(기둥들))]
        self.짝들 = [(a, b) for a in 팔 for b in 기둥] + [(팔[0], 팔[2])]   # 팔-기둥, 위팔-손목
        self.검사_수 = 0

    def 거리(self, q: np.ndarray) -> float:
        """자세 q에서 짝들 사이의 가장 짧은 거리(m)."""
        self.검사_수 += 1
        self.데이터.qpos[:] = q
        mujoco.mj_kinematics(self.모델, self.데이터)        # 위치만 계산(힘·접촉은 건너뛴다)
        return min(mujoco.mj_geomDistance(self.모델, self.데이터, a, b, 1.0, None) for a, b in self.짝들)

    def 충돌(self, q: np.ndarray) -> bool:
        return self.거리(q) < self.여유

    def 선분_충돌(self, q1: np.ndarray, q2: np.ndarray, 간격: float = 0.03) -> bool:
        """관절 공간의 곧은 선을 간격(rad)마다 검사한다(13.1절 팔공간.py와 같은 방식)."""
        개수 = int(np.ceil(np.linalg.norm(q2 - q1) / 간격)) + 1
        return any(self.충돌(q1 + t * (q2 - q1)) for t in np.linspace(0, 1, 개수))
