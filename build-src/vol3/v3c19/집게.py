"""15장: 손가락 두 개짜리 평행 집게를 MJCF 조각으로 만든다."""

손가락_최대 = 0.04       # 손가락 하나가 가운데에서 벌어질 수 있는 거리(m). 최대 너비 8cm
TCP = 0.06               # 손바닥 기준 집는 점(TCP)까지의 거리(m): 손가락 끝 쪽 가운데


def 집게_몸체(위치: str = "0 0 0", 마찰: float = 1.0) -> str:
    """부모 몸체의 +z 쪽으로 뻗은 집게(hand). 손가락은 y축을 따라 마주 보고 미끄러진다."""
    손가락 = """
      <body name="finger_{0}" pos="0 {1}0.006 0.02" gravcomp="1">
        <joint name="finger_{0}" type="slide" axis="0 {1}1 0" range="0 {2}" damping="10" armature="0.01"/>
        <geom name="pad_{0}" type="box" pos="0 0 0.03" size="0.01 0.006 0.03" friction="{3} 0.005 0.0001"
              mass="0.02" rgba="0.2 0.2 0.25 1"/>
        <site name="touch_{0}" type="box" pos="0 {4}0.006 0.03" size="0.011 0.002 0.031" rgba="0 0 0 0"/>
      </body>"""
    return f"""
    <body name="hand" pos="{위치}" gravcomp="1">
    <geom name="palm" type="box" pos="0 0 0.01" size="0.02 0.05 0.01" mass="0.1" rgba="0.3 0.3 0.35 1"/>
    <site name="tcp" pos="0 0 {TCP}" size="0.006" rgba="1 0.2 0.2 1"/>
    <site name="wrist_ft" pos="0 0 0"/>{손가락.format("l", "", 손가락_최대, 마찰, "-")}{손가락.format("r", "-", 손가락_최대, 마찰, "")}
    </body>"""


def 집게_부속(쥐는_힘: float = 10.0) -> str:
    """두 손가락을 묶는 제약, 벌림 너비를 재는 힘줄, 액추에이터, 센서."""
    return f"""
  <equality><joint joint1="finger_l" joint2="finger_r"/></equality>
  <tendon>
    <fixed name="width"><joint joint="finger_l" coef="1"/><joint joint="finger_r" coef="1"/></fixed>
  </tendon>
  <actuator>
    <position name="grip" tendon="width" kp="2000" dampratio="1" ctrlrange="0 {2 * 손가락_최대}"
              forcelimited="true" forcerange="-{쥐는_힘} {쥐는_힘}"/>
  </actuator>
  <sensor>
    <touch name="touch_l" site="touch_l"/>
    <touch name="touch_r" site="touch_r"/>
    <tendonpos name="width" tendon="width"/>
    <force name="wrist_force" site="wrist_ft"/>
    <torque name="wrist_torque" site="wrist_ft"/>
  </sensor>"""
