"""10장: 핀홀 카메라 만들기, 투영, 두 대 이상의 카메라로 삼각측량(DLT)."""
import numpy as np


def 바라보기(위치_세계, 바라볼점_세계) -> np.ndarray:
    """카메라를 놓은 자리에서 한 점을 보게 하는 R_세계_카메라. 열 = 카메라 축을 세계에서 본 방향."""
    z = np.asarray(바라볼점_세계, float) - np.asarray(위치_세계, float)   # 광학 좌표: z 앞
    z /= np.linalg.norm(z)
    x = np.cross(z, [0.0, 0.0, 1.0])                                     # x 오른쪽
    x /= np.linalg.norm(x)
    return np.column_stack([x, np.cross(z, x), z])                      # y 아래


def 카메라_만들기(위치_세계, 바라볼점_세계, 초점_px: float = 600.0,
              너비: int = 640, 높이: int = 480) -> np.ndarray:
    """세계 점을 픽셀로 옮기는 3×4 투영 행렬 P = K [R_카메라_세계 | t]."""
    R_카메라_세계 = 바라보기(위치_세계, 바라볼점_세계).T
    t = -R_카메라_세계 @ np.asarray(위치_세계, float)
    K = np.array([[초점_px, 0, (너비 - 1) / 2],          # 주점: 픽셀 가운데 약속(9장)
                  [0, 초점_px, (높이 - 1) / 2],
                  [0, 0, 1]])
    return K @ np.column_stack([R_카메라_세계, t])


def 투영(P: np.ndarray, 점들_세계: np.ndarray) -> np.ndarray:
    """N×3 세계 점 → N×2 픽셀. 동차 좌표로 곱한 뒤 깊이로 나눈다."""
    동차 = np.column_stack([점들_세계, np.ones(len(점들_세계))]) @ P.T
    return 동차[:, :2] / 동차[:, 2:3]


def 삼각측량(P들: list[np.ndarray], 픽셀들: list[np.ndarray]) -> np.ndarray:
    """카메라마다 한 픽셀씩 본 같은 점의 3D 위치. 직접 선형 변환(DLT)과 SVD로 푼다."""
    줄들 = []
    for P, (u, v) in zip(P들, 픽셀들):
        줄들.append(u * P[2] - P[0])          # u = (P0·X) / (P2·X) 를 0 = ... 꼴로
        줄들.append(v * P[2] - P[1])
    _, _, Vt = np.linalg.svd(np.array(줄들))
    X = Vt[-1]                                # A X = 0 의 가장 그럴듯한 답
    return X[:3] / X[3]
