"""10장 실습: 벽에 달린 세로 평면 2링크 팔(3장 두링크.py의 0.4m, 0.3m)과 목표를 보여 주는 반투명 팔."""
from 두링크 import 아래팔, 위팔


def 팔_몸체(이름: str, 색: str, 실물: bool) -> str:
    """관절 축은 -y: 정면(-y 쪽)에서 보면 x 오른쪽, z 위인 평면에서 반시계로 돈다."""
    접촉 = "" if 실물 else ' contype="0" conaffinity="0"'
    return f"""
    <body name="{이름}_위팔" pos="0 0 1.2" gravcomp="1">
      <joint name="{이름}_어깨" type="hinge" axis="0 -1 0" damping="0.5"/>
      <geom type="capsule" fromto="0 0 0 {위팔} 0 0" size="0.035" rgba="{색}"{접촉}/>
      <body name="{이름}_아래팔" pos="{위팔} 0 0" gravcomp="1">
        <joint name="{이름}_팔꿈치" type="hinge" axis="0 -1 0" damping="0.5"/>
        <geom type="capsule" fromto="0 0 0 {아래팔} 0 0" size="0.03" rgba="{색}"{접촉}/>
      </body>
    </body>"""


XML = f"""
<mujoco>
  <option timestep="0.002"/>
  <asset>
    <texture type="skybox" builtin="gradient" rgb1="0.95 0.95 1" rgb2="0.6 0.7 0.8" width="256" height="256"/>
  </asset>
  <worldbody>
    <light pos="0 -2 3" dir="0 0.5 -1"/>
    <camera name="정면" pos="0.2 -1.7 1.45" xyaxes="1 0 0 0 0 1"/>
    <geom type="box" pos="-0.06 0.05 1.0" size="0.04 0.04 0.3" rgba="0.4 0.4 0.4 1"/>
    {팔_몸체("로봇", "0.2 0.5 0.9 1", True)}
    {팔_몸체("목표", "1 0.55 0.1 0.45", False)}
  </worldbody>
  <actuator>
    <position joint="로봇_어깨" kp="100" dampratio="1"/>
    <position joint="로봇_팔꿈치" kp="100" dampratio="1"/>
  </actuator>
</mujoco>"""
