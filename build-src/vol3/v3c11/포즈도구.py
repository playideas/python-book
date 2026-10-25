"""11장: 평면 포즈 (x, y, θ)와 3×3 동차 변환을 오가는 도구."""
import numpy as np


def 각도_정리(각):
    """각도를 -π ~ π 사이로 맞춘다(359도와 -1도를 같은 값으로)."""
    return (np.asarray(각) + np.pi) % (2 * np.pi) - np.pi


def 포즈_행렬(포즈) -> np.ndarray:
    """포즈 (x, y, θ)를 3×3 동차 변환으로. 2장의 4×4를 평면으로 줄인 것."""
    x, y, 각 = 포즈
    c, s = np.cos(각), np.sin(각)
    return np.array([[c, -s, x],
                     [s, c, y],
                     [0, 0, 1.0]])


def 행렬_포즈(T: np.ndarray) -> np.ndarray:
    """3×3 동차 변환을 포즈 (x, y, θ)로."""
    return np.array([T[0, 2], T[1, 2], np.arctan2(T[1, 0], T[0, 0])])


def 점_옮기기(T: np.ndarray, 점들: np.ndarray) -> np.ndarray:
    """N×2 점들을 T로 옮긴다. T_방_로봇과 로봇 기준 점들이면 방 기준 점들이 된다."""
    return 점들 @ T[:2, :2].T + T[:2, 2]


def 상대_포즈(포즈_가, 포즈_나) -> np.ndarray:
    """가에서 본 나의 포즈. 2장의 역변환(가) @ 나를 평면에서."""
    return 행렬_포즈(np.linalg.inv(포즈_행렬(포즈_가)) @ 포즈_행렬(포즈_나))


def 포즈_잇기(포즈, 증분) -> np.ndarray:
    """포즈에서 자기 기준으로 증분만큼 움직인 다음 포즈."""
    return 행렬_포즈(포즈_행렬(포즈) @ 포즈_행렬(증분))


def 포즈_쌓기(시작_포즈, 증분들) -> np.ndarray:
    """시작 포즈에 증분들을 차례로 이어 붙인 포즈 열(N+1×3). 추측 항법."""
    포즈들 = [np.asarray(시작_포즈, dtype=float)]
    for 증분 in 증분들:
        포즈들.append(포즈_잇기(포즈들[-1], 증분))
    return np.array(포즈들)
