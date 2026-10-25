"""10장 실습: 손을 흔드는 사람의 참값 3D 키포인트와, 두 카메라가 잰 잡음 섞인 픽셀(예제용)."""
import numpy as np

from 사람모델 import 키포인트_3d
from 카메라도구 import 카메라_만들기, 투영

초당_프레임 = 30
시간 = np.arange(0, 4, 1 / 초당_프레임)          # 4초, 120프레임
카메라들 = [카메라_만들기([3.0, 1.2, 1.3], [0, 0, 1.2]),     # 사람의 왼쪽 앞
          카메라_만들기([3.0, -1.2, 1.3], [0, 0, 1.2])]    # 사람의 오른쪽 앞


def 오른팔_각(t: float) -> list[float]:
    """[옆들기, 앞들기, 비틀기, 팔꿈치](rad). 팔꿈치를 1.5Hz로 흔들고 어깨도 천천히 오르내린다."""
    return [np.deg2rad(120 + 8 * np.sin(2 * np.pi * 0.5 * t)), 0.0, np.deg2rad(-90),
            np.deg2rad(60 + 35 * np.sin(2 * np.pi * 1.5 * t))]


def 참_키포인트() -> np.ndarray:
    """프레임마다 17×3 키포인트. 모양 (120, 17, 3)."""
    return np.array([키포인트_3d(오른팔_각=오른팔_각(t), 왼팔_각=[np.deg2rad(10), 0, 0, np.deg2rad(20)])
                     for t in 시간])


def 잰_픽셀(잡음_px: float = 2.0, 씨앗: int = 0) -> list[np.ndarray]:
    """카메라마다 (120, 17, 2) 픽셀. 검출기의 떨림을 정규 분포 잡음으로 흉내 낸다."""
    생성기 = np.random.default_rng(씨앗)
    참값 = 참_키포인트()
    return [np.array([투영(P, 점들) for 점들 in 참값]) + 생성기.normal(0, 잡음_px, (len(시간), 17, 2))
            for P in 카메라들]
