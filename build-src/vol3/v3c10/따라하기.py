"""10장: 사람 오른팔의 3D 키포인트를 평면 2링크 로봇 팔(3장 두링크.py)의 관절 각도로 옮기는 도구."""
import numpy as np

from 골격도구 import 번호
from 두링크 import 아래팔, 위팔, 역기구학2
from 사람모델 import 아래팔_길이, 위팔_길이
from 카메라도구 import 삼각측량

배율 = (위팔 + 아래팔) / (위팔_길이 + 아래팔_길이)      # 로봇 팔 길이 ÷ 사람 팔 길이


def 평면_좌표(점: np.ndarray, 어깨: np.ndarray) -> np.ndarray:
    """오른팔이 움직이는 몸 앞쪽 평면(y-z)의 2D 좌표. 가로 = 바깥쪽(-y), 세로 = 위(+z)."""
    d = np.asarray(점) - 어깨
    return np.array([-d[1], d[2]])


def 사람_팔_각(어깨: np.ndarray, 팔꿈치: np.ndarray, 손목: np.ndarray) -> np.ndarray:
    """관절 매핑: 평면에서 잰 [어깨 각, 팔꿈치 각](rad). 로봇 관절 각도와 같은 약속이다."""
    위 = 평면_좌표(팔꿈치, 어깨)
    아래 = 평면_좌표(손목, 어깨) - 위
    어깨_각 = np.arctan2(위[1], 위[0])
    팔꿈치_각 = np.arctan2(위[0] * 아래[1] - 위[1] * 아래[0], 위 @ 아래)    # 위팔에서 아래팔까지 돈 각
    return np.array([어깨_각, 팔꿈치_각])


def 손끝_매핑(어깨: np.ndarray, 손목: np.ndarray, 기준_각: np.ndarray) -> np.ndarray:
    """손끝 매핑: 손목 위치를 로봇 크기로 늘려 역기구학으로 푼다. 답이 둘이면 기준_각에 가까운 쪽."""
    목표 = 평면_좌표(손목, 어깨) * 배율
    답들 = 역기구학2(목표)
    if not 답들:                                   # 닿지 않으면 팔이 닿는 끝까지만
        목표 = 목표 / np.linalg.norm(목표) * (위팔 + 아래팔) * 0.999
        답들 = 역기구학2(목표)
    return min(답들, key=lambda q: np.linalg.norm(q - 기준_각))


def 오른팔_복원(P들: list[np.ndarray], 픽셀들: list[np.ndarray]) -> np.ndarray:
    """카메라마다 (프레임, 17, 2) 픽셀 → 프레임마다 오른어깨·팔꿈치·손목 3D 위치 (프레임, 3, 3)."""
    세_점 = [번호["오른어깨"], 번호["오른팔꿈치"], 번호["오른손목"]]
    return np.array([[삼각측량(P들, [픽셀[k, i] for 픽셀 in 픽셀들]) for i in 세_점]
                     for k in range(len(픽셀들[0]))])


def 저역통과(값들: np.ndarray, 알파: float) -> np.ndarray:
    """10.6절의 1차 저역통과를 첫 번째 축(시간)을 따라 배열 전체에 적용한다."""
    결과 = [값들[0]]
    for 값 in 값들[1:]:
        결과.append(결과[-1] + 알파 * (값 - 결과[-1]))
    return np.array(결과)
