"""13장: 11장에서 만든 점유 격자 지도를 불러와 로봇 크기만큼 장애물을 부풀린다."""
import numpy as np
from scipy import ndimage

from 격자도구 import 지도_만들기, 지도_원점, 해상도
from 주행데이터 import 주행_기록

로봇_반지름 = 0.2          # m. 11장 방장면의 로봇(원기둥 반지름 0.2m)


def 막힌_칸() -> np.ndarray:
    """11장 11.4절의 '참 포즈로 85개' 지도. 찬칸과 모르는 칸(확률 0.5 이상)을 막힌 칸으로 본다."""
    참_포즈들, _, 스캔들 = 주행_기록()
    return 지도_만들기(참_포즈들, 스캔들).확률() >= 0.5


def 부풀리기(막힘: np.ndarray, 반지름: float) -> np.ndarray:
    """막힌 칸에서 반지름 이내인 칸까지 막는다. 남은 '통과' 칸에는 로봇 중심을 둘 수 있다."""
    벽까지_거리 = ndimage.distance_transform_edt(~막힘) * 해상도     # 칸마다 가장 가까운 막힌 칸까지(m)
    return 벽까지_거리 > 반지름


def 칸(점) -> tuple[int, int]:
    """방 좌표(m) → 칸 번호 (i, j)."""
    i, j = np.floor((np.asarray(점) - 지도_원점) / 해상도).astype(int)
    return int(i), int(j)


def 점들(칸들) -> np.ndarray:
    """칸 번호들 → 칸 가운데의 방 좌표(m)."""
    return (np.asarray(칸들, dtype=float) + 0.5) * 해상도 + 지도_원점
