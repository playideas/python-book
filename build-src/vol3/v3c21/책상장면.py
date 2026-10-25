"""21장: 15장의 집게 단 팔 앞 책상에 물건 여러 개, 정리 상자 둘, 연필꽂이를 놓는다(19장 지시장면.py를 고친 것)."""
from dataclasses import dataclass

import mujoco
import numpy as np

from 집게 import 집게_몸체, 집게_부속
from 팔도구 import 예제_팔
from 팔집게장면 import 글, 받침_위치

높이, 너비 = 480, 640
카메라_fovy = 50
카메라_위치 = np.array([0.95, 0.0, 0.95])     # 19장과 같은 머리 카메라: 책상 앞쪽 위에서 로봇 쪽을 본다
카메라_목표 = np.array([0.38, -0.02, 0.40])
R_광학_mj = np.diag([1, -1, -1])
책상_높이 = 받침_위치[2]                       # 0.4m

# 종류(색) → (반크기(m), rgba). 빨강·초록은 정리할 물건, 파랑은 규칙에 없는 물건
종류들 = {"빨강": ([0.03, 0.02, 0.02], "0.85 0.12 0.1 1"),
         "초록": ([0.025, 0.0175, 0.025], "0.15 0.65 0.2 1"),
         "파랑": ([0.025, 0.025, 0.015], "0.15 0.35 0.85 1"),
         "노랑": ([0.025, 0.025, 0.02], "0.95 0.8 0.1 1")}     # 노랑은 카메라 보정용 블록
상자들 = {"빨강": np.array([0.215, -0.29]), "초록": np.array([0.425, -0.29])}   # 종류별 정리 상자 가운데(책상에 고정)
상자_안쪽, 상자_벽_높이 = 0.085, 0.03         # 안쪽 반너비 8.5cm(안쪽 17×17cm), 벽 높이 3cm
칸들 = [np.array([-0.045, 0.0]), np.array([0.045, 0.0])]   # 상자 안 놓을 자리 두 칸(상자 가운데 기준, 물건 길이를 x로)
연필꽂이 = (np.array([0.37, -0.10]), 0.035, 0.20)   # 가운데, 반지름, 높이(m): 물건과 상자 사이를 막는다
대기_자세 = np.deg2rad([180, 30, 90, 0, 60, 0])     # 사진 찍을 때 팔을 뒤로 돌려 둔다(19장의 찍는 자세)


@dataclass(frozen=True)
class 물성:
    """시뮬과 '현실 역할'이 다를 수 있는 숫자들(20장 20.1절의 생각을 책상에)."""
    물건_마찰: float = 0.5
    패드_마찰: float = 1.0
    질량_배율: float = 1.0
    밝기: float = 1.0
    깊이_잡음: float = 0.0                       # 깊이 표준편차(m)
    카메라_틀어짐: tuple = (0.0, 0.0, 0.0)        # 실제 카메라 위치가 아는 값에서 벗어난 양(m)


def 바라보기(위치, 목표) -> np.ndarray:
    """위치에서 목표를 보는 카메라의 R_세계_광학(9장)."""
    z = np.asarray(목표, float) - 위치
    z /= np.linalg.norm(z)
    x = np.cross(z, [0, 0, 1])
    x /= np.linalg.norm(x)
    return np.column_stack([x, np.cross(z, x), z])


def 무작위_배치(생성기, 개수={"빨강": 2, "초록": 2, "파랑": 0}, 간격: float = 0.10) -> list[dict]:
    """책상 앞쪽(x 0.28~0.52, y 0~0.26m)에 물건을 서로 간격 이상 떨어뜨려 놓는다."""
    물건들 = []
    for 종류, 수 in 개수.items():
        for _ in range(수):
            while True:
                위치 = 생성기.uniform([0.28, 0.0], [0.52, 0.26])
                if all(np.linalg.norm(위치 - 다른["위치"]) > 간격 for 다른 in 물건들):
                    break
            물건들.append({"이름": f"{종류}{len(물건들)}", "종류": 종류, "위치": 위치,
                        "요": float(생성기.uniform(-90, 90))})
    return 물건들


def 물건_xml(물건: dict, p: 물성) -> str:
    반크기, 색 = 종류들[물건["종류"]]
    return (f'<body name="{물건["이름"]}" pos="{글(물건["위치"])} {책상_높이 + 반크기[2]}" '
            f'euler="0 0 {물건["요"]:.2f}"><freejoint/><geom name="{물건["이름"]}" type="box" size="{글(반크기)}" '
            f'mass="{0.1 * p.질량_배율}" rgba="{색}" contype="1" friction="{p.물건_마찰} 0.005 0.0001"/></body>')


def 상자_xml(종류: str) -> str:
    """바닥판 하나와 벽 넷으로 만든 열린 상자(책상에 붙어 있다)."""
    a, h, 두께 = 상자_안쪽, 상자_벽_높이, 0.005
    벽들 = [(a + 두께, 0, 두께, a + 2 * 두께), (-a - 두께, 0, 두께, a + 2 * 두께),
           (0, a + 두께, a, 두께), (0, -a - 두께, a, 두께)]
    return (f'<body name="상자_{종류}" pos="{글(상자들[종류])} {책상_높이}"><geom type="box" size="{a} {a} 0.0025" '
            f'pos="0 0 0.0025"/>' + "".join(f'<geom type="box" pos="{x} {y} {h / 2}" size="{sx} {sy} {h / 2}"/>'
                                           for x, y, sx, sy in 벽들) + "</body>")


def 장면_xml(물건들: list[dict], p: 물성 = 물성()) -> str:
    몸체들 = []
    for i, (_, 위치, 축) in enumerate(예제_팔):
        다음 = 예제_팔[i + 1][1] if i + 1 < len(예제_팔) else [0, 0, 0.03]
        몸체들.append(f'<body name="link{i + 1}" pos="{글(위치)}" gravcomp="1"><joint name="joint{i + 1}" '
                    f'axis="{글(축)}"/><geom type="capsule" fromto="0 0 0 {글(다음)}" size="0.02" rgba="0.8 0.5 0.2 1"/>')
    실제_위치 = 카메라_위치 + np.asarray(p.카메라_틀어짐)
    R_mj = 바라보기(실제_위치, 카메라_목표 + np.asarray(p.카메라_틀어짐)) @ R_광학_mj
    (펜_x, 펜_y), 펜_r, 펜_h = 연필꽂이
    return f"""
<mujoco model="책상 정리 팔">
  <option timestep="0.002" integrator="implicitfast" cone="elliptic" impratio="10"/>
  <visual><global offwidth="{너비}" offheight="{높이}"/>
    <headlight diffuse="{0.4 * p.밝기:.3f} {0.4 * p.밝기:.3f} {0.4 * p.밝기:.3f}" ambient="{0.1 * p.밝기:.3f} {0.1 * p.밝기:.3f} {0.1 * p.밝기:.3f}"/></visual>
  <asset>
    <texture type="skybox" builtin="gradient" rgb1="0.95 0.95 1" rgb2="0.6 0.7 0.8" width="256" height="256"/>
    <texture name="격자" type="2d" builtin="checker" rgb1="0.25 0.3 0.35" rgb2="0.75 0.75 0.75" width="256" height="256"/>
    <material name="바닥재" texture="격자" texrepeat="8 8"/>
  </asset>
  <default>
    <joint type="hinge" damping="1" armature="0.05"/>
    <geom contype="2" conaffinity="1"/>
    <position kp="400" dampratio="1"/>
    <default class="상자"><geom contype="1" rgba="0.82 0.82 0.85 1"/></default>
  </default>
  <worldbody>
    <light pos="0.6 -0.4 2.5" dir="-0.1 0.15 -1" diffuse="{0.8 * p.밝기:.3f} {0.8 * p.밝기:.3f} {0.8 * p.밝기:.3f}"/>
    <camera name="머리" pos="{글(실제_위치)}" xyaxes="{글(R_mj[:, 0])} {글(R_mj[:, 1])}" fovy="{카메라_fovy}"/>
    <geom name="floor" type="plane" size="2 2 0.1" material="바닥재" contype="1"/>
    <geom name="table" type="box" pos="0.35 0 0.2" size="0.45 0.5 0.2" rgba="0.75 0.6 0.45 1"
          contype="1" friction="0.5 0.005 0.0001"/>
    <geom name="연필꽂이" type="cylinder" pos="{펜_x} {펜_y} {책상_높이 + 펜_h / 2}" size="{펜_r} {펜_h / 2}"
          rgba="0.35 0.3 0.3 1" contype="1"/>
    <body name="base" pos="{글(받침_위치)}">
      <geom type="cylinder" fromto="0 0 0 0 0 0.1" size="0.05" rgba="0.3 0.3 0.3 1"/>
      {"".join(몸체들)}{집게_몸체("0 0 0.05", p.패드_마찰)}{"</body>" * len(예제_팔)}
    </body>
    {"".join(물건_xml(물건, p) for 물건 in 물건들)}
    <frame childclass="상자">{상자_xml("빨강")}{상자_xml("초록")}</frame>
  </worldbody>
  <actuator>
    {"".join(f'<position name="joint{i + 1}" joint="joint{i + 1}"/>' for i in range(len(예제_팔)))}
  </actuator>
  {집게_부속()}
</mujoco>"""


def 찍기(모델, 데이터, p: 물성 = 물성(), 생성기=None) -> tuple[np.ndarray, np.ndarray]:
    """지금 상태 그대로 컬러와 깊이(광학 z, m)를 찍는다. 팔을 대기 자세에 두는 것은 부르는 쪽의 일이다."""
    with mujoco.Renderer(모델, 높이, 너비) as 그리개:
        그리개.update_scene(데이터, camera="머리")
        컬러 = 그리개.render()
        그리개.enable_depth_rendering()
        그리개.update_scene(데이터, camera="머리")
        깊이 = 그리개.render()
    if p.깊이_잡음 > 0:
        깊이 = 깊이 + (생성기 or np.random.default_rng(0)).normal(0, p.깊이_잡음, 깊이.shape)
    return 컬러, 깊이
