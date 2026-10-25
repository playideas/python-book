"""9장: 탁자 위 물체 장면과 카메라 계산 도구."""
import cv2
import mujoco
import numpy as np

from 회전도구 import Ry

높이, 너비 = 480, 640                        # 찍을 사진 크기(픽셀)
머리_fovy = 60                               # 머리 카메라의 세로 시야각(도)
R_몸_광학 = np.array([[0, 0, 1], [-1, 0, 0], [0, -1, 0]])   # 2장 2.3절의 축 바꾸기
R_광학_mj = np.diag([1, -1, -1])            # MuJoCo 카메라 축(x 오른쪽, y 위, -z를 봄)을 광학 축으로
R_로봇_머리 = Ry(40) @ R_몸_광학             # 머리 카메라: 40도 숙여 탁자를 본다(광학 축)
머리_위치_로봇 = np.array([0.0, 0.0, 0.45])  # 로봇 바닥판 위 0.45m

# 정답: 물체 이름 → (세계 기준 중심 위치, 반지름, MuJoCo geom 문자열)
물체들 = {
    "빨강": ([0.45, 0.12, 0.80], 0.035, 'type="cylinder" size="0.035 0.05" rgba="0.85 0.1 0.1 1"'),
    "초록": ([0.55, -0.10, 0.78], 0.03, 'type="box" size="0.03 0.03 0.03" rgba="0.1 0.7 0.2 1"'),
    "파랑": ([0.38, -0.06, 0.785], 0.035, 'type="sphere" size="0.035" rgba="0.1 0.3 0.9 1"'),
    "노랑": ([0.62, 0.10, 0.81], 0.025, 'type="cylinder" size="0.025 0.06" rgba="0.95 0.8 0.1 1"'),
}


def 변환(R: np.ndarray, p) -> np.ndarray:
    """회전 R과 이동 p를 4×4 동차 변환 행렬로 묶는다(2장 2.8절)."""
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = p
    return T


def 바라보기(위치, 목표) -> np.ndarray:
    """위치에서 목표를 보는 카메라의 R_세계_광학. 사진의 아래쪽이 세계의 아래쪽을 향한다."""
    z = np.asarray(목표, float) - 위치
    z /= np.linalg.norm(z)
    x = np.cross(z, [0, 0, 1])
    x /= np.linalg.norm(x)
    return np.column_stack([x, np.cross(z, x), z])


def 축_글자(R_광학: np.ndarray) -> str:
    """광학 축 회전을 MuJoCo 카메라의 xyaxes 여섯 숫자로 적는다."""
    R_mj = R_광학 @ R_광학_mj
    return " ".join(f"{v:.6f}" for v in np.concatenate([R_mj[:, 0], R_mj[:, 1]]))


def 장면_xml(추가: str = "", 자산: str = "") -> str:
    """탁자(윗면 높이 0.75m), 로봇 바닥판, 머리 카메라, 색깔 물체 넷이 있는 장면."""
    물체_xml = "\n".join(f'<body name="{이름}" pos="{" ".join(map(str, p))}"><geom name="{이름}" {g}/></body>'
                       for 이름, (p, _, g) in 물체들.items())
    return f"""
<mujoco>
  <visual><global offwidth="{너비}" offheight="{높이}"/></visual>
  <asset>
    <texture name="격자" type="2d" builtin="checker" rgb1="0.3 0.3 0.35" rgb2="0.5 0.5 0.55" width="64" height="64"/>
    <material name="바닥재" texture="격자" texrepeat="8 8"/>
    {자산}
  </asset>
  <worldbody>
    <light pos="0.5 0 2.5" dir="0 0 -1" diffuse="0.7 0.7 0.7"/>
    <light pos="-0.5 0 1.8" dir="1 0 -1" diffuse="0.4 0.4 0.4" castshadow="false"/>
    <geom type="plane" size="3 3 0.1" material="바닥재"/>
    <geom name="탁자" type="box" pos="0.55 0 0.375" size="0.35 0.5 0.375" rgba="0.85 0.85 0.82 1"/>
    <body name="로봇" pos="0 0 0.75">
      <geom type="cylinder" size="0.08 0.02" pos="0 0 0.02" rgba="0.2 0.2 0.25 1"/>
      <camera name="머리" pos="{" ".join(map(str, 머리_위치_로봇))}" xyaxes="{축_글자(R_로봇_머리)}" fovy="{머리_fovy}"/>
    </body>
    {물체_xml}
    {추가}
  </worldbody>
</mujoco>"""


def K_만들기(fovy_도: float, 높이: int = 높이, 너비: int = 너비) -> np.ndarray:
    """세로 시야각으로 내부 행렬 K를 만든다. 픽셀 가운데를 정수 좌표로 보는 OpenCV 약속."""
    f = (높이 / 2) / np.tan(np.deg2rad(fovy_도) / 2)
    return np.array([[f, 0, (너비 - 1) / 2],
                     [0, f, (높이 - 1) / 2],
                     [0, 0, 1]])


def T_세계_카메라(데이터: mujoco.MjData, 이름: str) -> np.ndarray:
    """MuJoCo 카메라의 포즈를 광학 좌표계(x 오른쪽, y 아래, z 앞)로 돌려준다."""
    카메라 = 데이터.camera(이름)
    return 변환(카메라.xmat.reshape(3, 3) @ R_광학_mj, 카메라.xpos)


def 찍기(모델: mujoco.MjModel, 데이터: mujoco.MjData, 카메라: str) -> tuple[np.ndarray, np.ndarray]:
    """컬러 사진(RGB, uint8)과 깊이 영상(m, float32)을 함께 찍는다."""
    mujoco.mj_forward(모델, 데이터)
    with mujoco.Renderer(모델, 높이, 너비) as 렌더러:
        렌더러.update_scene(데이터, camera=카메라)
        컬러 = 렌더러.render()
        렌더러.enable_depth_rendering()
        렌더러.update_scene(데이터, camera=카메라)
        깊이 = 렌더러.render()
    return 컬러, 깊이


def png_바이트(이미지: np.ndarray) -> bytes:
    """MuJoCo 텍스처로 넘길 PNG 파일 내용을 메모리에서 만든다."""
    return cv2.imencode(".png", 이미지)[1].tobytes()
