"""15장: 집게만 위아래로 움직이는 시험대. 탁자 위 상자를 집어 들어 본다."""
import mujoco

from 집게 import 손가락_최대, 집게_몸체, 집게_부속

탁자_높이 = 0.4
상자_높이 = 0.05


def 시험대_xml(쥐는_힘: float = 10.0, 상자_질량: float = 0.2, 상자_x: float = 0.0, 상자_y: float = 0.0,
            옵션: str = 'cone="elliptic" impratio="10"', 묶기: bool = True, 들기_kp: float = 2000) -> str:
    """집게는 수직 slide 관절(lift) 하나로 오르내린다. lift = 0이면 TCP가 상자 가운데 높이."""
    부속 = 집게_부속(쥐는_힘)
    if not 묶기:
        부속 = 부속.replace('<equality><joint joint1="finger_l" joint2="finger_r"/></equality>', "")
    TCP_시작 = 탁자_높이 + 상자_높이 / 2
    return f"""
<mujoco>
  <option timestep="0.002" integrator="implicitfast" {옵션}/>
  <asset>
    <texture type="skybox" builtin="gradient" rgb1="0.95 0.95 1" rgb2="0.6 0.7 0.8" width="256" height="256"/>
  </asset>
  <worldbody>
    <light pos="-0.6 -0.3 1.2" dir="0.6 0.3 -0.8"/>
    <geom name="table" type="box" pos="0 0 0.2" size="0.3 0.3 0.2" friction="0.5 0.005 0.0001" rgba="0.75 0.6 0.45 1"/>
    <body name="lifter" pos="0 0 {TCP_시작 + 0.06}" quat="0 1 0 0" gravcomp="1">
      <joint name="lift" type="slide" axis="0 0 -1"/>
      {집게_몸체()}
    </body>
    <body name="box" pos="{상자_x} {상자_y} {TCP_시작}">
      <freejoint/>
      <geom name="box" type="box" size="0.04 0.025 {상자_높이 / 2}" mass="{상자_질량}" friction="0.5 0.005 0.0001"
            rgba="0.95 0.75 0.1 1"/>
    </body>
  </worldbody>
  <actuator><position name="lift" joint="lift" kp="{들기_kp}" dampratio="1"/></actuator>
  {부속}
</mujoco>"""


def 만들기(**설정) -> tuple[mujoco.MjModel, mujoco.MjData]:
    """시험대를 만들고 집게를 활짝 연 채로 시작한다."""
    모델 = mujoco.MjModel.from_xml_string(시험대_xml(**설정))
    데이터 = mujoco.MjData(모델)
    for 손가락 in ("finger_l", "finger_r"):
        데이터.joint(손가락).qpos = 손가락_최대
    데이터.ctrl[모델.actuator("grip").id] = 2 * 손가락_최대
    mujoco.mj_forward(모델, 데이터)
    return 모델, 데이터


def 흘려보내기(모델, 데이터, 초: float, 매번=None) -> None:
    """초만큼 시간을 흘린다. 매번(데이터)을 주면 걸음마다 부른다."""
    끝 = 데이터.time + 초
    while 데이터.time < 끝 - 1e-9:
        if 매번 is not None:
            매번(데이터)
        mujoco.mj_step(모델, 데이터)


def 들기(모델, 데이터, 높이: float, 초: float = 1.0) -> None:
    """집게를 지금 높이에서 '높이'(m)까지 초 동안 부드럽게(3s² - 2s³) 옮기고 0.5초 기다린다."""
    시작, 처음 = 데이터.time, 데이터.ctrl[모델.actuator("lift").id]

    def 한_걸음(d) -> None:
        s = min((d.time - 시작) / 초, 1.0)
        d.ctrl[모델.actuator("lift").id] = 처음 + (높이 - 처음) * (3 * s**2 - 2 * s**3)

    흘려보내기(모델, 데이터, 초 + 0.5, 한_걸음)
