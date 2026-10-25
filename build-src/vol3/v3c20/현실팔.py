"""20장: 같은 코드로 '시뮬'과 '현실 역할'을 만드는 세로 2관절 팔. 각도 0은 수평, 양수는 위로."""
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass

import mujoco
import numpy as np

L1, L2 = 0.30, 0.25                      # 위팔·아래팔 길이(m), 12장 세로 팔과 같다
주기 = 0.01                               # 제어 주기(초), 100Hz
토크_한계 = np.array([20.0, 8.0])         # 명령으로 보낼 수 있는 토크(N·m)
관절들 = ["shoulder", "elbow"]


@dataclass(frozen=True)
class 물성:
    """시뮬과 현실이 다를 수 있는 숫자들. 기본값이 우리가 처음 적은 '시뮬' 팔이다."""
    끝_질량: float = 0.4       # 손끝 공의 질량(kg)
    감쇠: float = 0.5          # 관절 점성 감쇠(N·m·s/rad)
    마찰: float = 0.0          # 관절 마른 마찰(N·m), 기어가 뻑뻑한 정도
    토크_배율: float = 1.0     # 모터가 실제로 내는 토크 / 명령한 토크
    지연: int = 0              # 명령이 모터에 닿기까지 걸리는 제어 주기 수
    잡음: float = 0.0          # 각도 측정 잡음의 표준편차(rad)
    유격: float = 0.0          # 기어 유격, 한쪽 방향 크기(rad)


시뮬_물성 = 물성()
# 정답지: '현실 역할' 팔. 20.3절에서 맞춰 볼 때까지는 모르는 척한다
현실_물성 = 물성(끝_질량=0.55, 감쇠=0.3, 마찰=0.25, 토크_배율=0.85, 지연=2,
               잡음=np.deg2rad(0.3), 유격=np.deg2rad(0.5))


def 장면(p: 물성) -> str:
    """관절마다 모터 쪽 관절(엔코더가 재는 곳)을 두고, 유격이 있으면 그 뒤에 헐거운 관절을 하나 더 둔다."""
    def 유격_관절(이름: str) -> str:
        if p.유격 == 0:
            return ""
        return (f'<joint name="{이름}_유격" type="hinge" axis="0 -1 0" limited="true" '
                f'range="{-p.유격} {p.유격}" damping="0.002"/>')
    작은_몸 = '<geom type="sphere" size="0.01" mass="0.01" contype="0" conaffinity="0"/>'
    return f"""
<mujoco model="세로 2관절 팔">
  <option timestep="0.001" integrator="implicitfast"/>
  <default><joint type="hinge" axis="0 -1 0" armature="0.01"/>
    <geom contype="0" conaffinity="0"/></default>
  <worldbody>
    <body name="base" pos="0 0 0.8">
      <body name="shoulder_motor">
        <joint name="shoulder" damping="{p.감쇠}" frictionloss="{p.마찰}"/>{작은_몸}
        <body name="upper">{유격_관절("shoulder")}
          <geom type="capsule" fromto="0 0 0 {L1} 0 0" size="0.025" mass="1.0"/>
          <body name="elbow_motor" pos="{L1} 0 0">
            <joint name="elbow" damping="{p.감쇠}" frictionloss="{p.마찰}"/>{작은_몸}
            <body name="lower">{유격_관절("elbow")}
              <geom type="capsule" fromto="0 0 0 {L2} 0 0" size="0.02" mass="0.6"/>
              <geom type="sphere" pos="{L2} 0 0" size="0.035" mass="{p.끝_질량}"/>
              <site name="tip" pos="{L2} 0 0"/>
            </body>
          </body>
        </body>
      </body>
    </body>
  </worldbody>
  <actuator>
    <motor joint="shoulder" gear="{p.토크_배율}" ctrlrange="{-토크_한계[0]} {토크_한계[0]}"/>
    <motor joint="elbow" gear="{p.토크_배율}" ctrlrange="{-토크_한계[1]} {토크_한계[1]}"/>
  </actuator>
</mujoco>"""


def 참_각도(모델: mujoco.MjModel, 데이터: mujoco.MjData) -> np.ndarray:
    """링크가 실제로 놓인 각도 = 모터 쪽 각도 + 유격 안에서 밀린 만큼."""
    각도 = np.array([데이터.joint(이름).qpos[0] for 이름 in 관절들])
    if mujoco.mj_name2id(모델, mujoco.mjtObj.mjOBJ_JOINT, "shoulder_유격") >= 0:
        각도 += [데이터.joint(f"{이름}_유격").qpos[0] for 이름 in 관절들]
    return 각도


def 실행(제어기: Callable, 시간: float, p: 물성 = 시뮬_물성, 시드: int = 0,
       시작: tuple[float, float] = (-np.pi / 2, 0.0)) -> dict[str, np.ndarray]:
    """주기마다 잰 각도를 제어기(t, 잰_각도)에 주고 받은 토크를 (지연 뒤에) 모터에 건다."""
    모델 = mujoco.MjModel.from_xml_string(장면(p))
    데이터 = mujoco.MjData(모델)
    for 이름, 값 in zip(관절들, 시작):
        데이터.joint(이름).qpos[0] = 값
    mujoco.mj_forward(모델, 데이터)
    생성기 = np.random.default_rng(시드)
    대기열 = deque([np.zeros(2)] * p.지연)                    # 아직 모터에 닿지 않은 명령들
    기록 = {"시각": [], "잰_각도": [], "참_각도": [], "토크": []}
    for k in range(round(시간 / 주기)):
        t = k * 주기
        모터_각도 = np.array([데이터.joint(이름).qpos[0] for 이름 in 관절들])
        잰_각도 = 모터_각도 + 생성기.normal(0, p.잡음, 2) if p.잡음 > 0 else 모터_각도
        토크 = np.clip(제어기(t, 잰_각도), -토크_한계, 토크_한계)
        대기열.append(토크)
        데이터.ctrl[:] = 대기열.popleft()
        for 이름, 값 in zip(기록, [t, 잰_각도, 참_각도(모델, 데이터), 토크]):
            기록[이름].append(값)
        for _ in range(round(주기 / 모델.opt.timestep)):
            mujoco.mj_step(모델, 데이터)
    return {이름: np.array(값) for 이름, 값 in 기록.items()}


def 중력_토크(p: 물성) -> Callable[[np.ndarray], np.ndarray]:
    """물성 p라고 믿는 팔 모델로, 각도 q에서 중력을 버티는 데 필요한 토크를 계산하는 함수."""
    모델 = mujoco.MjModel.from_xml_string(장면(물성(끝_질량=p.끝_질량)))
    데이터 = mujoco.MjData(모델)

    def 계산(q: np.ndarray) -> np.ndarray:
        데이터.qpos[:] = q
        mujoco.mj_forward(모델, 데이터)
        return 데이터.qfrc_bias.copy()
    return 계산
