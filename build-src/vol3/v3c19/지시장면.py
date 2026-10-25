"""19장: 15장의 집게 단 팔 앞 탁자에 물체 넷과 파란 그릇을 놓고, 머리 카메라로 찍는다."""
import mujoco
import numpy as np

from 집게 import 집게_몸체, 집게_부속
from 팔도구 import 예제_팔
from 팔집게장면 import 글, 받침_위치

높이, 너비 = 480, 640                        # 사진 크기(픽셀)
카메라_fovy = 50                             # 머리 카메라의 세로 시야각(도)
카메라_위치 = np.array([0.95, 0.0, 0.95])     # 탁자 앞쪽 위에서 로봇 쪽을 내려다본다
카메라_목표 = np.array([0.38, -0.02, 0.40])
R_광학_mj = np.diag([1, -1, -1])            # MuJoCo 카메라 축 ↔ 광학 축(9장 9.2절)
탁자_높이 = 받침_위치[2]                      # 0.4m

# 이름 → (모양, 반크기(m), 색 rgba, 탁자 위 (x, y), 요(도)). 반크기는 MuJoCo size 그대로
물체들 = {
    "빨간 상자": ("box", [0.04, 0.025, 0.025], "0.85 0.12 0.1 1", (0.42, 0.12), 30),
    "초록 상자": ("box", [0.035, 0.025, 0.03], "0.15 0.65 0.2 1", (0.52, -0.08), -20),
    "빨간 공": ("sphere", [0.03], "0.85 0.12 0.1 1", (0.32, 0.12), 0),
    "노란 컵": ("cylinder", [0.025, 0.04], "0.95 0.8 0.1 1", (0.62, 0.18), 0),
}
그릇_중심 = np.array([0.3, -0.25])           # 15장의 놓을 곳 자리에 둥근 그릇을 붙여 둔다
그릇_반지름, 그릇_벽_높이 = 0.08, 0.04


def 바라보기(위치, 목표) -> np.ndarray:
    """위치에서 목표를 보는 카메라의 R_세계_광학(9장). 사진 아래쪽이 세계 아래쪽을 향한다."""
    z = np.asarray(목표, float) - 위치
    z /= np.linalg.norm(z)
    x = np.cross(z, [0, 0, 1])
    x /= np.linalg.norm(x)
    return np.column_stack([x, np.cross(z, x), z])


def 물체_xml(이름: str, 모양: str, 반크기, 색: str, 위치, 요: float) -> str:
    z = 탁자_높이 + (반크기[0] if 모양 == "sphere" else 반크기[-1])     # 바닥이 탁자에 닿게
    return (f'<body name="{이름}" pos="{글(위치)} {z}" euler="0 0 {요}"><freejoint/>'
            f'<geom name="{이름}" type="{모양}" size="{글(반크기)}" mass="0.1" rgba="{색}" contype="1" '
            f'friction="0.5 0.005 0.0001"/></body>')


def 그릇_xml() -> str:
    """바닥판 하나와 짧은 벽 조각 16개로 만든 둥근 그릇(탁자에 붙어 있다)."""
    벽들 = "".join(f'<geom type="box" size="0.005 0.017 {그릇_벽_높이 / 2}" pos="{그릇_반지름 * np.cos(각):.4f} '
                  f'{그릇_반지름 * np.sin(각):.4f} {그릇_벽_높이 / 2}" euler="0 0 {np.rad2deg(각):.2f}"/>'
                  for 각 in np.linspace(0, 2 * np.pi, 16, endpoint=False))
    return (f'<body name="그릇" pos="{글(그릇_중심)} {탁자_높이}"><geom name="그릇_바닥" type="cylinder" '
            f'size="{그릇_반지름} 0.0025" pos="0 0 0.0025"/>{벽들}</body>')


def 장면_xml(물체=물체들) -> str:
    몸체들 = []
    for i, (_, 위치, 축) in enumerate(예제_팔):
        다음 = 예제_팔[i + 1][1] if i + 1 < len(예제_팔) else [0, 0, 0.03]
        몸체들.append(f'<body name="link{i + 1}" pos="{글(위치)}" gravcomp="1"><joint name="joint{i + 1}" '
                    f'axis="{글(축)}"/><geom type="capsule" fromto="0 0 0 {글(다음)}" size="0.02" rgba="0.8 0.5 0.2 1"/>')
    R_mj = 바라보기(카메라_위치, 카메라_목표) @ R_광학_mj
    return f"""
<mujoco model="말로 시키는 팔">
  <option timestep="0.002" integrator="implicitfast" cone="elliptic" impratio="10"/>
  <visual><global offwidth="{너비}" offheight="{높이}"/></visual>
  <asset>
    <texture type="skybox" builtin="gradient" rgb1="0.95 0.95 1" rgb2="0.6 0.7 0.8" width="256" height="256"/>
    <texture name="격자" type="2d" builtin="checker" rgb1="0.25 0.3 0.35" rgb2="0.75 0.75 0.75" width="256" height="256"/>
    <material name="바닥재" texture="격자" texrepeat="8 8"/>
  </asset>
  <default>
    <joint type="hinge" damping="1" armature="0.05"/>
    <geom contype="2" conaffinity="1"/>
    <position kp="400" dampratio="1"/>
    <default class="그릇"><geom contype="1" rgba="0.15 0.35 0.85 1"/></default>
  </default>
  <worldbody>
    <light pos="0.6 -0.4 2.5" dir="-0.1 0.15 -1" diffuse="0.8 0.8 0.8"/>
    <camera name="머리" pos="{글(카메라_위치)}" xyaxes="{글(R_mj[:, 0])} {글(R_mj[:, 1])}" fovy="{카메라_fovy}"/>
    <geom name="floor" type="plane" size="2 2 0.1" material="바닥재" contype="1"/>
    <geom name="table" type="box" pos="0.35 0 0.2" size="0.45 0.5 0.2" rgba="0.75 0.6 0.45 1"
          contype="1" friction="0.5 0.005 0.0001"/>
    <body name="base" pos="{글(받침_위치)}">
      <geom type="cylinder" fromto="0 0 0 0 0 0.1" size="0.05" rgba="0.3 0.3 0.3 1"/>
      {"".join(몸체들)}{집게_몸체("0 0 0.05")}{"</body>" * len(예제_팔)}
    </body>
    {"".join(물체_xml(이름, *값) for 이름, 값 in 물체.items())}
    <frame childclass="그릇">{그릇_xml()}</frame>
  </worldbody>
  <actuator>
    {"".join(f'<position name="joint{i + 1}" joint="joint{i + 1}"/>' for i in range(len(예제_팔)))}
  </actuator>
  {집게_부속()}
</mujoco>"""


def 찍기(모델: mujoco.MjModel, 데이터: mujoco.MjData) -> tuple[np.ndarray, np.ndarray]:
    """팔을 뒤로 돌려 카메라 앞을 비우고 컬러 사진과 깊이(광학 z, m)를 함께 찍는다."""
    데이터.qpos[:6] = np.deg2rad([180, 30, 90, 0, 60, 0])
    mujoco.mj_forward(모델, 데이터)
    with mujoco.Renderer(모델, 높이, 너비) as 그리개:
        그리개.update_scene(데이터, camera="머리")
        컬러 = 그리개.render()
        그리개.enable_depth_rendering()
        그리개.update_scene(데이터, camera="머리")
        깊이 = 그리개.render()
    return 컬러, 깊이
