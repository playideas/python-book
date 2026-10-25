"""8장: 경첩에 매달려 앞뒤로 기우는 판. IMU는 경첩 위 0.3m에 달려 있다."""
import mujoco
import numpy as np

장면 = """
<mujoco>
  <worldbody>
    <body name="판" pos="0 0 0.5">
      <joint name="피치" type="hinge" axis="0 1 0"/>
      <geom type="box" size="0.15 0.1 0.02" mass="1"/>
      <geom type="capsule" fromto="0 0 0 0 0 0.3" size="0.015" mass="0.2"/>
      <site name="imu" pos="0 0 0.3"/>
    </body>
  </worldbody>
  <actuator><motor joint="피치"/></actuator>
  <sensor>
    <gyro name="자이로" site="imu"/>
    <accelerometer name="가속도" site="imu"/>
  </sensor>
</mujoco>
"""
주기 = 0.01                     # 센서를 읽는 간격(100Hz)


def 목표(t: float) -> tuple[float, float]:
    """판이 따라갈 피치 각도와 각속도. 12~16초에는 빠르게 덜덜 떤다."""
    각도 = 0.3 * np.sin(0.5 * t)
    각속도 = 0.15 * np.cos(0.5 * t)
    if 12 <= t < 16:                         # 떨림의 크기는 0에서 시작해 커졌다가 다시 0이 된다
        크기, 크기_변화 = 0.06 * np.sin(np.pi * (t - 12) / 4), 0.06 * np.pi / 4 * np.cos(np.pi * (t - 12) / 4)
        각도 += 크기 * np.sin(10 * (t - 12))
        각속도 += 크기_변화 * np.sin(10 * (t - 12)) + 10 * 크기 * np.cos(10 * (t - 12))
    return 각도, 각속도


def 기록하기(초: float = 30.0) -> dict[str, np.ndarray]:
    """판을 흔들며 100Hz로 참 피치, 자이로 y, 가속도 x·z를 기록한다(잡음 없는 값)."""
    모델 = mujoco.MjModel.from_xml_string(장면)
    데이터 = mujoco.MjData(모델)
    한번에 = round(주기 / 모델.opt.timestep)
    기록 = {"시간": [], "참_피치": [], "자이로": [], "가속도": []}
    for k in range(round(초 / 모델.opt.timestep)):
        각도, 각속도 = 목표(데이터.time)
        데이터.ctrl[0] = 8 * (각도 - 데이터.qpos[0]) + 0.8 * (각속도 - 데이터.qvel[0])
        mujoco.mj_step(모델, 데이터)
        if (k + 1) % 한번에 == 0:
            mujoco.mj_forward(모델, 데이터)          # 4장 4.7절: 걸음을 마친 상태로 센서를 다시 계산
            기록["시간"].append(데이터.time)
            기록["참_피치"].append(데이터.qpos[0])
            기록["자이로"].append(데이터.sensor("자이로").data[1])
            기록["가속도"].append(데이터.sensor("가속도").data[[0, 2]])
    return {이름: np.array(값) for 이름, 값 in 기록.items()}


def 센서_더하기(기록: dict, 생성기: np.random.Generator, 자이로_잡음: float = 0.01,
            자이로_치우침: float = 0.02, 가속도_잡음: float = 0.5) -> tuple[np.ndarray, np.ndarray]:
    """깨끗한 기록에 값싼 IMU의 잡음(표준편차)과 치우침을 더한다. 단위는 rad/s, m/s²."""
    n = len(기록["시간"])
    자이로 = 기록["자이로"] + 자이로_치우침 + 생성기.normal(0, 자이로_잡음, n)
    가속도 = 기록["가속도"] + 생성기.normal(0, 가속도_잡음, (n, 2))
    return 자이로, 가속도


def 가속도_피치(가속도: np.ndarray) -> np.ndarray:
    """중력 방향으로 읽은 피치(7장 7.9절의 식). 가속도는 [x, z] 열."""
    return np.arctan2(-가속도[..., 0], 가속도[..., 1])


def rms_도(오차_rad: np.ndarray) -> float:
    """오차의 제곱 평균 제곱근을 도 단위로."""
    return float(np.rad2deg(np.sqrt(np.mean(np.square(오차_rad)))))
