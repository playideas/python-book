"""20.6절: 9장의 탁자 장면을 조명·색·카메라 잡음을 바꿔 찍고, 빨간 컵의 정답 마스크도 함께 얻는다."""
import cv2
import mujoco
import numpy as np

from 비전장면 import 높이, 너비, 장면_xml
from 색찾기 import 색_범위


class 조명카메라:
    def __init__(self):
        self.모델 = mujoco.MjModel.from_xml_string(장면_xml())
        self.데이터 = mujoco.MjData(self.모델)
        mujoco.mj_forward(self.모델, self.데이터)
        self.렌더러 = mujoco.Renderer(self.모델, 높이, 너비)
        self.원래_조명 = self.모델.light_diffuse.copy()      # 9장 장면의 두 조명
        self.컵 = self.모델.geom("빨강").id
        self.원래_컵색 = self.모델.geom_rgba[self.컵].copy()

    def 찍기(self, 밝기: float = 1.0, 색조=(1.0, 1.0, 1.0), 잡음: float = 0.0, 컵색_흔들기: float = 0.0,
           생성기: np.random.Generator | None = None) -> tuple[np.ndarray, np.ndarray]:
        """조명 밝기·색조, 픽셀 잡음(표준편차), 컵 색 흔들기를 적용한 사진과 컵의 정답 마스크."""
        생성기 = 생성기 or np.random.default_rng(0)
        빛 = 밝기 * np.asarray(색조)
        self.모델.light_diffuse[:] = self.원래_조명 * 빛
        self.모델.vis.headlight.diffuse[:] = 0.4 * 빛            # 9장 장면의 기본 머리 조명도 함께
        self.모델.vis.headlight.ambient[:] = 0.1 * 빛
        self.모델.geom_rgba[self.컵, :3] = np.clip(
            self.원래_컵색[:3] + 생성기.uniform(-컵색_흔들기, 컵색_흔들기, 3), 0, 1)
        self.렌더러.update_scene(self.데이터, camera="머리")
        컬러 = self.렌더러.render().astype(float)
        컬러 = np.clip(컬러 + 생성기.normal(0, 잡음, 컬러.shape), 0, 255).astype(np.uint8) if 잡음 > 0 else 컬러.astype(np.uint8)
        self.렌더러.enable_segmentation_rendering()             # 픽셀마다 어느 geom인지 알려 주는 정답지
        self.렌더러.update_scene(self.데이터, camera="머리")
        정답 = self.렌더러.render()[..., 0] == self.컵
        self.렌더러.disable_segmentation_rendering()
        return 컬러, 정답


def 빨강_마스크(컬러: np.ndarray, s_최소: int, v_최소: int) -> np.ndarray:
    """9장의 빨강 색상(H) 범위는 그대로 두고, 채도·밝기의 아래 문턱만 바꿔 찾는다."""
    hsv = cv2.cvtColor(컬러, cv2.COLOR_RGB2HSV)
    마스크 = np.zeros(hsv.shape[:2], np.uint8)
    for 아래, 위 in 색_범위["빨강"]:
        마스크 |= cv2.inRange(hsv, np.array([아래[0], s_최소, v_최소]), np.array(위))
    return cv2.morphologyEx(마스크, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0


def IoU(찾은: np.ndarray, 정답: np.ndarray) -> float:
    """겹친 넓이 / 합친 넓이. 1이면 정답과 똑같다."""
    return float((찾은 & 정답).sum() / max((찾은 | 정답).sum(), 1))
