"""21장: 손가락이 늘 아래를 보는 자세만으로 13장의 RRT를 돌려, 장애물을 피하는 관절 경로를 만든다."""
import mujoco
import numpy as np

from 경로도구 import 관절_경로
from 집게 import TCP, 집게_몸체
from 책상장면 import 상자_xml, 연필꽂이, 책상_높이
from 팔도구 import 예제_팔
from 팔집게장면 import 글, 받침_위치
from 표본계획 import RRT, 지름길

여유 = 0.02                     # 장애물과 이만큼(m) 가까우면 부딪힌 것으로 친다(13장 13.7절의 여유)
v최대 = 1.0                     # 관절 최대 속도(rad/s)
하한 = np.deg2rad([-120, -30, 0, -360])      # 상태 = (허리, 어깨, 팔꿈치, 집게 요)의 표본 범위
상한 = np.deg2rad([200, 120, 150, 360])


def 관절로(c) -> np.ndarray:
    """상태 4개 → 관절 6개. 손목1 = 0, 어깨 + 팔꿈치 + 손목2 = 180도면 손가락이 바로 아래를 본다."""
    허리, 어깨, 팔꿈치, 요 = c
    return np.array([허리, 어깨, 팔꿈치, 0.0, np.pi - 어깨 - 팔꿈치, 허리 + np.pi - 요])


def 상태로(q) -> np.ndarray:
    return np.array([q[0], q[1], q[2], q[0] + np.pi - q[5]])


def 계획_xml(장애물: list[dict], 든_것: dict | None) -> str:
    """계획 전용 모델: 로봇 몸(contype 1)과 세상(conaffinity 1)만 서로 닿는지 본다. 세상에는 여유를 준다."""
    몸체들 = "".join(f'<body name="link{i + 1}" pos="{글(위치)}"><joint axis="{글(축)}"/><geom type="capsule" '
                  f'fromto="0 0 0 {글(예제_팔[i + 1][1] if i + 1 < len(예제_팔) else [0, 0, 0.03])}" size="0.02"/>'
                  for i, (_, 위치, 축) in enumerate(예제_팔))
    손 = 집게_몸체("0 0 0.05")
    if 든_것 is not None:                     # 들고 있는 물건은 손의 일부: TCP에 물건 가운데가 온다
        반 = [든_것["길이"] / 2, 든_것["폭"] / 2, 든_것["높이"] / 2]
        손 = 손[:손.rfind("</body>")] + f'<geom type="box" pos="0 0 {TCP}" size="{글(반)}"/></body>'
    물건들 = "".join(f'<geom type="box" pos="{글(물건["중심"])}" euler="0 0 {물건["요_도"]:.1f}" '
                  f'size="{글([물건["길이"] / 2, 물건["폭"] / 2, 물건["높이"] / 2])}"/>' for 물건 in 장애물)
    (펜_x, 펜_y), 펜_r, 펜_h = 연필꽂이
    return f"""
<mujoco><default><joint type="hinge"/><geom contype="1" conaffinity="0"/>
  <default class="세상"><geom contype="0" conaffinity="1" margin="{여유}"/></default></default>
  <worldbody>
    <frame childclass="세상">
      <geom type="box" pos="0.35 0 0.2" size="0.45 0.5 0.2"/>
      <geom type="cylinder" pos="{펜_x} {펜_y} {책상_높이 + 펜_h / 2}" size="{펜_r} {펜_h / 2}"/>
      {상자_xml("빨강")}{상자_xml("초록")}{물건들}
    </frame>
    <body pos="{글(받침_위치)}">{몸체들}{손}{"</body>" * len(예제_팔)}</body>
  </worldbody>
</mujoco>"""


class 충돌검사기:
    def __init__(self, 장애물: list[dict], 든_것: dict | None = None):
        self.모델 = mujoco.MjModel.from_xml_string(계획_xml(장애물, 든_것))
        self.데이터 = mujoco.MjData(self.모델)
        self.손가락 = (든_것["폭"] / 2 + 0.002) if 든_것 else 0.04      # 쥐고 있으면 물건 폭만큼 벌어져 있다
        self.검사_수 = 0

    def 충돌(self, c) -> bool:
        """상태 c에서 몸과 세상이 여유 안으로 들어오는가. 13장처럼 짝마다 묻지 않고 접촉 판정 한 번으로."""
        self.검사_수 += 1
        self.데이터.qpos[:6] = 관절로(c)
        self.데이터.qpos[6:8] = self.손가락
        mujoco.mj_kinematics(self.모델, self.데이터)
        mujoco.mj_collision(self.모델, self.데이터)
        return self.데이터.ncon > 0

    def 선분_충돌(self, c1, c2, 간격: float = 0.03) -> bool:
        개수 = int(np.ceil(np.linalg.norm(c2 - c1) / 간격)) + 1
        return any(self.충돌(c1 + t * (c2 - c1)) for t in np.linspace(0, 1, 개수))


def 계획(q_시작, q_끝, 검사기: 충돌검사기, 생성기) -> list[np.ndarray] | None:
    """곧게 갈 수 있으면 곧게, 막혔으면 RRT + 지름길(13장). 100Hz 관절 목표 목록, 길이 없으면 None."""
    c_시작, c_끝 = 상태로(q_시작), 상태로(q_끝)
    if not 검사기.선분_충돌(c_시작, c_끝):
        경유점 = [c_시작, c_끝]                 # 관절 공간의 곧은 선(손끝은 휘어 간다)
    else:
        경유점, _, _, _ = RRT(c_시작, c_끝, 검사기.선분_충돌, 하한, 상한, 생성기, 걸음=0.3, 최대_반복=3000)
        if 경유점 is None:
            return None
        경유점 = 지름길(경유점, 검사기.선분_충돌, 생성기)
    검사기.경유점_수 = len(경유점)
    경로, q = [], 관절로(경유점[0])
    for c in 경유점[1:]:                       # 경유점마다 멈췄다 간다. 가장 많이 도는 관절이 v최대를 넘지 않게
        다음 = 관절로(c)
        경로 += 관절_경로(q, 다음, max(0.3, 1.5 * np.abs(다음 - q).max() / v최대))
        q = 다음
    return 경로
