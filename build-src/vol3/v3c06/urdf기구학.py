"""URDF를 읽어 순기구학을 계산한다. robot_state_publisher가 안에서 하는 일을 파이썬으로."""
import numpy as np
from scipy.spatial.transform import Rotation

from 팔도구 import 변환, 이동, 축_회전


def 원점_변환(origin) -> np.ndarray:
    """joint의 <origin xyz rpy>: 고정 축 롤→피치→요, 곧 Rz(요) @ Ry(피치) @ Rx(롤) (2장 2.4절)."""
    if origin is None:                                   # origin을 안 적으면 제자리
        return np.eye(4)
    xyz = origin.xyz or [0.0, 0.0, 0.0]
    rpy = origin.rpy or [0.0, 0.0, 0.0]
    return 변환(Rotation.from_euler("xyz", rpy).as_matrix(), xyz)


def 관절_움직임(관절, 값: float) -> np.ndarray:
    """관절 값만큼의 움직임: 회전 관절은 축을 중심으로 돌고, 직선 관절은 축을 따라 미끄러진다."""
    축 = np.array(관절.axis if 관절.axis is not None else [1.0, 0.0, 0.0])   # axis 기본값은 x축
    if 관절.type in ("revolute", "continuous"):
        return 축_회전(축, 값)
    if 관절.type == "prismatic":
        return 이동(축 * 값)
    return np.eye(4)                                     # fixed


def URDF_순기구학(로봇, 관절값: dict[str, float], 끝: str, 시작: str | None = None) -> np.ndarray:
    """시작 링크(기본은 뿌리)에서 끝 링크까지 joint를 따라가며 곱한 T_시작_끝."""
    시작 = 시작 or 로봇.get_root()
    T = np.eye(4)
    for 이름 in 로봇.get_chain(시작, 끝, links=False):    # 지나가는 joint 이름들
        관절 = 로봇.joint_map[이름]
        T = T @ 원점_변환(관절.origin) @ 관절_움직임(관절, 관절값.get(이름, 0.0))
    return T
