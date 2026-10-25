"""11장: 벽과 기둥이 있는 방, 그리고 MuJoCo 레이 캐스팅으로 흉내 낸 2차원 라이다."""
import mujoco
import numpy as np

# 안쪽 크기 10m × 8m인 방. 가운데 섬을 로봇이 한 바퀴 돈다
방_XML = """
<mujoco>
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
    <geom type="cylinder" pos="0.7 0.7 0.5" size="0.25 0.5" rgba="0.8 0.45 0.3 1"/>
    <geom type="cylinder" pos="5 0.6 0.5" size="0.2 0.5" rgba="0.8 0.45 0.3 1"/>
    <geom type="cylinder" pos="9.2 4.3 0.5" size="0.3 0.5" rgba="0.8 0.45 0.3 1"/>
    <geom type="cylinder" pos="0.7 5.3 0.5" size="0.2 0.5" rgba="0.8 0.45 0.3 1"/>
    <geom type="box" pos="2.6 7.6 0.4" size="0.6 0.3 0.4" rgba="0.6 0.5 0.35 1"/>
    <geom type="box" pos="8.9 0.5 0.4" size="0.4 0.4 0.4" rgba="0.6 0.5 0.35 1"/>
    <geom type="box" pos="7.4 7.7 0.4" size="0.3 0.2 0.4" rgba="0.6 0.5 0.35 1"/>
    <body name="robot" mocap="true">
      <geom type="cylinder" size="0.2 0.1" pos="0 0 0.1" rgba="0.2 0.6 0.3 1"/>
      <geom type="box" size="0.08 0.04 0.03" pos="0.14 0 0.22" rgba="0.95 0.95 0.95 1"/>
    </body>
  </worldbody>
</mujoco>
"""

레이_수 = 180                                   # 기본값: 한 바퀴를 2도 간격으로 잰다
최대_거리 = 8.0                                 # m. 이보다 먼 벽은 돌아오지 않는다
라이다_높이 = 0.3                               # m. 바닥과 나란히 쏜다


def 방_만들기() -> tuple[mujoco.MjModel, mujoco.MjData]:
    모델 = mujoco.MjModel.from_xml_string(방_XML)
    return 모델, mujoco.MjData(모델)


def 로봇_놓기(모델: mujoco.MjModel, 데이터: mujoco.MjData, 포즈) -> None:
    """mocap 몸체인 로봇을 포즈 (x, y, θ)에 옮겨 놓는다."""
    x, y, 각 = 포즈
    데이터.mocap_pos[0] = [x, y, 0.0]
    데이터.mocap_quat[0] = [np.cos(각 / 2), 0.0, 0.0, np.sin(각 / 2)]   # z축 회전, [w x y z]
    mujoco.mj_forward(모델, 데이터)


def 레이_각도(개수: int) -> np.ndarray:
    """레이 방향(rad): 로봇 앞(+x)에서 시작해 반시계로 같은 간격."""
    return np.arange(개수) * 2 * np.pi / 개수


def 라이다_스캔(모델: mujoco.MjModel, 데이터: mujoco.MjData, 포즈,
             생성기: np.random.Generator | None = None, 잡음: float = 0.0,
             개수: int = 레이_수) -> np.ndarray:
    """포즈 (x, y, θ)에서 한 바퀴 잰 거리(m). 돌아오지 않은 레이는 nan."""
    로봇_놓기(모델, 데이터, 포즈)
    x, y, 각 = 포즈
    각도들 = 각 + 레이_각도(개수)
    방향들 = np.stack([np.cos(각도들), np.sin(각도들), np.zeros(개수)], axis=1)
    거리 = np.zeros(개수)
    기하_번호 = np.zeros(개수, dtype=np.int32)              # 레이마다 맞은 모양의 번호가 담긴다
    mujoco.mj_multiRay(모델, 데이터, np.array([x, y, 라이다_높이]), 방향들.ravel(), None, True,
                       모델.body("robot").id, 기하_번호, 거리, None, 개수, 최대_거리)
    거리[(거리 < 0) | (거리 > 최대_거리)] = np.nan          # 닿은 곳이 없으면 -1이 돌아온다
    if 생성기 is not None and 잡음 > 0:
        거리 = 거리 + 생성기.normal(0, 잡음, 개수)
    return 거리


def 스캔_점들(거리: np.ndarray) -> np.ndarray:
    """거리 배열을 로봇 기준 (x, y) 점구름(N×2)으로. 돌아오지 않은 레이는 뺀다."""
    각도들 = 레이_각도(len(거리))
    있음 = ~np.isnan(거리)
    return np.stack([거리[있음] * np.cos(각도들[있음]), 거리[있음] * np.sin(각도들[있음])], axis=1)
