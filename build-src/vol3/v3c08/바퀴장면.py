"""8.8절 실습: 바퀴 둘 달린 로봇, 얼음판, 위치를 아는 표지 네 개가 있는 MuJoCo 장면."""
import mujoco
import numpy as np

from 바퀴로봇 import 각도_감싸기, 표지_R, 표지_보기

표지들 = np.array([[-2.2, 2.6], [2.2, 2.6], [-2.2, -2.6], [2.2, -2.6]])   # 지도에 적힌 표지 위치(m)
바퀴_반지름, 바퀴_간격 = 0.05, 0.26           # 로봇이 알고 있는 치수(m)
한바퀴_눈금 = 4096                            # 바퀴 엔코더(7장의 STS3215와 같은 눈금 수)
주기, 표지_주기 = 0.1, 0.5                    # 오도메트리 10Hz, 표지 측정 2Hz
보는_거리, 보는_각 = 4.0, np.deg2rad(60)       # 카메라가 표지를 알아보는 범위

장면 = """
<mujoco>
  <option timestep="0.002" integrator="implicitfast"/>
  <worldbody>
    <light pos="0 0 5"/>
    <geom type="plane" size="4 4 0.1" rgba="0.85 0.85 0.8 1"/>
    <geom name="얼음" type="box" pos="1.2 1.2 0.0005" size="0.35 0.6 0.0005"
          friction="0.02 0.005 0.0001" priority="1" rgba="0.6 0.8 1 1"/>
    {표지}
    <body name="로봇" pos="0 0 0.05">
      <freejoint/>
      <geom type="box" size="0.12 0.1 0.03" pos="0 0 0.02" mass="2" rgba="0.9 0.5 0.1 1"/>
      <geom type="sphere" size="0.02" pos="-0.1 0 -0.04" condim="1" mass="0.05"/>
      <body name="왼바퀴" pos="0 0.13 0">
        <joint name="왼쪽" type="hinge" axis="0 1 0" armature="0.001"/>
        <geom type="cylinder" size="0.05 0.01" euler="90 0 0" mass="0.2" rgba="0.2 0.2 0.2 1"/>
      </body>
      <body name="오른바퀴" pos="0 -0.13 0">
        <joint name="오른쪽" type="hinge" axis="0 1 0" armature="0.001"/>
        <geom type="cylinder" size="0.05 0.01" euler="90 0 0" mass="0.2" rgba="0.2 0.2 0.2 1"/>
      </body>
    </body>
  </worldbody>
  <actuator>
    <velocity name="왼쪽" joint="왼쪽" kv="2"/>
    <velocity name="오른쪽" joint="오른쪽" kv="2"/>
  </actuator>
  <sensor>
    <jointpos name="왼쪽" joint="왼쪽"/>
    <jointpos name="오른쪽" joint="오른쪽"/>
  </sensor>
</mujoco>
"""


def 모델_만들기() -> mujoco.MjModel:
    """표지 기둥(부딪히지 않는 장식)을 넣어 모델을 만든다."""
    기둥 = "".join(f'<geom type="cylinder" pos="{x} {y} 0.25" size="0.06 0.25" contype="0" '
                 f'conaffinity="0" rgba="0.1 0.6 0.2 1"/>' for x, y in 표지들)
    return mujoco.MjModel.from_xml_string(장면.replace("{표지}", 기둥))


def 명령(t: float) -> tuple[float, float]:
    """8자 경로: 25초마다 왼쪽 원과 오른쪽 원(반지름 1.2m)을 번갈아 돈다. 속도는 출렁인다."""
    v = 0.3 + 0.15 * np.sin(3 * t)
    return v, (1 if (t // 25) % 2 == 0 else -1) * v / 1.2


def 방향(데이터: mujoco.MjData) -> float:
    w, x, y, z = 데이터.body("로봇").xquat
    return float(np.arctan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z)))


def 달리기(초: float, 생성기: np.random.Generator) -> dict:
    """로봇을 몰며 참 상태, 엔코더로 센 이동·회전, 표지 측정을 기록한다."""
    모델 = 모델_만들기()
    데이터 = mujoco.MjData(모델)
    mujoco.mj_forward(모델, 데이터)
    한번에 = round(주기 / 모델.opt.timestep)
    이전_눈금 = np.zeros(2)
    기록 = {"시간": [], "참": [], "오도": [], "표지": []}
    for k in range(round(초 / 모델.opt.timestep)):
        v, w = 명령(데이터.time)
        데이터.ctrl[:] = [(v - w * 바퀴_간격 / 2) / 바퀴_반지름, (v + w * 바퀴_간격 / 2) / 바퀴_반지름]
        mujoco.mj_step(모델, 데이터)
        if (k + 1) % 한번에:
            continue
        mujoco.mj_forward(모델, 데이터)
        각 = np.array([데이터.sensor("왼쪽").data[0], 데이터.sensor("오른쪽").data[0]])
        눈금 = np.floor(각 / (2 * np.pi) * 한바퀴_눈금)          # 엔코더는 다 채운 눈금만 센다
        왼, 오른 = (눈금 - 이전_눈금) * 2 * np.pi / 한바퀴_눈금 * 바퀴_반지름
        이전_눈금 = 눈금
        참 = np.array([*데이터.body("로봇").xpos[:2], 방향(데이터)])
        본_표지 = []
        if round(데이터.time / 주기) % round(표지_주기 / 주기) == 0:
            for i, 표지 in enumerate(표지들):
                z = 표지_보기(참, 표지) + 생성기.normal(0, np.sqrt(np.diag(표지_R)))
                if z[0] < 보는_거리 and abs(z[1]) < 보는_각:
                    본_표지.append((i, np.array([z[0], 각도_감싸기(z[1])])))
        기록["시간"].append(데이터.time)
        기록["참"].append(참)
        기록["오도"].append(((왼 + 오른) / 2, (오른 - 왼) / 바퀴_간격))
        기록["표지"].append(본_표지)
    기록["참"] = np.array(기록["참"])
    return 기록
