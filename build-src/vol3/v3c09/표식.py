"""9.6절: ArUco 표식을 장면에 붙이고, 사진에서 찾아 자세를 재는 도구."""
import cv2
import numpy as np
from scipy.spatial.transform import Rotation

from 비전장면 import png_바이트, 변환

사전 = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
표식_번호 = 7
변_길이 = 0.08                                   # 검은 테두리 바깥 변의 길이(m)


def 표식_조각(위치, 요_도: float = 0.0) -> tuple[str, str, dict]:
    """탁자에 붙일 표식의 (asset XML, body XML, 텍스처 파일 내용)."""
    픽셀 = 240
    그림 = np.full((픽셀 * 5 // 4, 픽셀 * 5 // 4), 255, np.uint8)       # 사방에 흰 여백
    여백 = 픽셀 // 8
    그림[여백:여백 + 픽셀, 여백:여백 + 픽셀] = cv2.aruco.generateImageMarker(사전, 표식_번호, 픽셀)
    반 = 변_길이 * 5 / 4 / 2
    자산 = '<texture name="표식" type="2d" file="aruco.png"/><material name="표식" texture="표식"/>'
    몸체 = (f'<body name="표식" pos="{" ".join(map(str, 위치))}" euler="0 0 {요_도}" mocap="true">'
          f'<geom type="box" size="{반} {반} 0.001" material="표식"/></body>')
    return 자산, 몸체, {"aruco.png": png_바이트(cv2.cvtColor(그림, cv2.COLOR_GRAY2RGB))}


_검출기 = cv2.aruco.ArucoDetector(사전, cv2.aruco.DetectorParameters())
_검출기_설정 = _검출기.getDetectorParameters()
_검출기_설정.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX    # 꼭짓점을 소수점 픽셀까지
_검출기.setDetectorParameters(_검출기_설정)
# 표식 기준 네 꼭짓점: 왼쪽 위, 오른쪽 위, 오른쪽 아래, 왼쪽 아래 (z=0, 가운데가 원점)
_꼭짓점_표식 = np.array([[-1, 1, 0], [1, 1, 0], [1, -1, 0], [-1, -1, 0]]) * 변_길이 / 2


def 표식_자세(컬러_rgb: np.ndarray, K: np.ndarray, 왜곡=None) -> np.ndarray | None:
    """사진에서 표식을 찾아 T_카메라_표식(4×4)을 돌려준다. 못 찾으면 None."""
    꼭짓점들, 번호들, _ = _검출기.detectMarkers(cv2.cvtColor(컬러_rgb, cv2.COLOR_RGB2GRAY))
    if 번호들 is None or 표식_번호 not in 번호들.ravel():
        return None
    꼭짓점 = 꼭짓점들[list(번호들.ravel()).index(표식_번호)][0]
    _, 회전벡터, 이동 = cv2.solvePnP(_꼭짓점_표식, 꼭짓점, K, 왜곡, flags=cv2.SOLVEPNP_IPPE_SQUARE)
    return 변환(cv2.Rodrigues(회전벡터)[0], 이동.ravel())


def 자세_차이(T_가: np.ndarray, T_나: np.ndarray) -> tuple[float, float]:
    """두 포즈의 위치 차이(cm)와 자세 차이(도)."""
    위치 = np.linalg.norm(T_가[:3, 3] - T_나[:3, 3]) * 100
    각도 = np.rad2deg(Rotation.from_matrix(T_가[:3, :3].T @ T_나[:3, :3]).magnitude())
    return float(위치), float(각도)
