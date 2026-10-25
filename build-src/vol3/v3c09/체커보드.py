"""9.3절: 체커보드를 여러 자세로 찍고, 알려진 렌즈 왜곡을 입히는 도구."""
import cv2
import mujoco
import numpy as np
from scipy.spatial.transform import Rotation

from 비전장면 import K_만들기, png_바이트

높이, 너비 = 480, 640
K_참 = K_만들기(50)                                   # 이 카메라의 진짜 내부 행렬
왜곡_참 = np.array([-0.28, 0.08, 0.0, 0.0, 0.0])      # 진짜 왜곡 계수 k1, k2, p1, p2, k3
칸_수 = (9, 7)                                         # 가로 9칸, 세로 7칸 → 안쪽 꼭짓점 8×6
칸_크기 = 0.03                                         # 한 칸 3cm
여유 = 1.4                                             # 왜곡을 입힐 때 가장자리까지 채우려고 넓게 찍는 비율


def 보드_그림(칸당_픽셀: int = 40) -> np.ndarray:
    """흰 테두리가 한 칸 두께로 둘러진 체커보드 이미지."""
    가로, 세로 = 칸_수
    그림 = np.full(((세로 + 2) * 칸당_픽셀, (가로 + 2) * 칸당_픽셀, 3), 255, np.uint8)
    for 행 in range(세로):
        for 열 in range(가로):
            if (행 + 열) % 2 == 0:
                그림[(행 + 1) * 칸당_픽셀:(행 + 2) * 칸당_픽셀, (열 + 1) * 칸당_픽셀:(열 + 2) * 칸당_픽셀] = 0
    return 그림


def 왜곡_입히기(넓은_사진: np.ndarray) -> np.ndarray:
    """왜곡 없는 넓은 사진에서, 왜곡_참을 가진 렌즈가 찍었을 사진을 만든다."""
    v, u = np.mgrid[0:높이, 0:너비].astype(np.float32)
    왜곡된_픽셀 = np.stack([u.ravel(), v.ravel()], axis=1)[:, None, :]
    정규 = cv2.undistortPoints(왜곡된_픽셀, K_참, 왜곡_참).reshape(높이, 너비, 2)   # 각 픽셀이 원래 있던 방향
    f, 넓은_cx, 넓은_cy = K_참[0, 0], (너비 * 여유 - 1) / 2, (높이 * 여유 - 1) / 2
    맵_x = (f * 정규[..., 0] + 넓은_cx).astype(np.float32)
    맵_y = (f * 정규[..., 1] + 넓은_cy).astype(np.float32)
    return cv2.remap(넓은_사진, 맵_x, 맵_y, cv2.INTER_LINEAR)


def 보드_사진들(개수: int, 퍼짐: float = 1.0, 거리=(0.45, 0.8), 왜곡: bool = True, 씨앗: int = 0) -> list[np.ndarray]:
    """카메라 앞 여러 자세의 체커보드를 찍는다. 퍼짐이 작으면 사진 가운데에만 놓인다."""
    넓은_높이, 넓은_너비 = int(높이 * 여유), int(너비 * 여유)
    반_가로, 반_세로 = (칸_수[0] + 2) * 칸_크기 / 2, (칸_수[1] + 2) * 칸_크기 / 2
    fovy = 2 * np.rad2deg(np.arctan(넓은_높이 / 2 / K_참[1, 1]))      # 초점 거리는 그대로, 시야만 넓게
    xml = f"""
<mujoco>
  <visual><global offwidth="{넓은_너비}" offheight="{넓은_높이}"/></visual>
  <asset><texture type="skybox" builtin="flat" rgb1="0.55 0.6 0.65" width="32" height="32"/>
    <texture name="보드" type="2d" file="board.png"/><material name="보드" texture="보드"/></asset>
  <worldbody>
    <light pos="0 0 2" dir="0 0 -1"/>
    <camera name="cam" pos="0 0 0" xyaxes="1 0 0 0 1 0" fovy="{fovy}"/>
    <body name="보드" mocap="true"><geom type="box" size="{반_가로} {반_세로} 0.002" material="보드"/></body>
  </worldbody>
</mujoco>"""
    모델 = mujoco.MjModel.from_xml_string(xml, assets={"board.png": png_바이트(보드_그림())})
    데이터 = mujoco.MjData(모델)
    생성기 = np.random.default_rng(씨앗)
    사진들 = []
    with mujoco.Renderer(모델, 넓은_높이, 넓은_너비) as 렌더러:
        for _ in range(개수):
            방향 = 생성기.uniform(-1, 1, 2) * [0.6, 0.45] * 퍼짐      # 보드 중심이 보이는 방향
            깊이 = 생성기.uniform(*거리)
            데이터.mocap_pos[0] = [*(방향 * 깊이), -깊이]
            기울기 = Rotation.from_euler("xyz", 생성기.uniform(-30, 30, 3) * [1, 1, 0.5], degrees=True)
            데이터.mocap_quat[0] = 기울기.as_quat(scalar_first=True)
            mujoco.mj_forward(모델, 데이터)
            렌더러.update_scene(데이터, camera="cam")
            넓은 = 렌더러.render()
            가운데 = 넓은[(넓은_높이 - 높이) // 2:][:높이, (넓은_너비 - 너비) // 2:][:, :너비]
            사진들.append(왜곡_입히기(넓은) if 왜곡 else 가운데.copy())
    return 사진들
