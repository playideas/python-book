"""9.7절: AX = XB를 풀어 손에 달린 카메라의 설치 포즈 X = T_손_카메라를 구한다."""
import numpy as np
from scipy.spatial.transform import Rotation

from 비전장면 import 변환


def 손눈_보정(손_자세들: list[np.ndarray], 표식_자세들: list[np.ndarray]) -> np.ndarray:
    """손_자세들은 T_세계_손, 표식_자세들은 T_카메라_표식. 같은 순간끼리 짝이다."""
    A들, B들 = [], []
    for i in range(len(손_자세들)):
        for j in range(i + 1, len(손_자세들)):
            A들.append(np.linalg.inv(손_자세들[j]) @ 손_자세들[i])        # 손이 움직인 양
            B들.append(표식_자세들[j] @ np.linalg.inv(표식_자세들[i]))    # 카메라가 움직인 양
    # 회전: 두 움직임의 회전 축은 R_X로 이어진다(α = R_X β). 축들을 가장 잘 겹치는 회전을 SVD로
    α = np.array([Rotation.from_matrix(A[:3, :3]).as_rotvec() for A in A들])
    β = np.array([Rotation.from_matrix(B[:3, :3]).as_rotvec() for B in B들])
    U, _, Vt = np.linalg.svd(β.T @ α)
    부호 = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])            # 거울상이 아닌 회전으로
    R_X = Vt.T @ 부호 @ U.T
    # 이동: (R_A - I) t_X = R_X t_B - t_A 를 모두 쌓아 최소제곱으로
    왼쪽 = np.vstack([A[:3, :3] - np.eye(3) for A in A들])
    오른쪽 = np.concatenate([R_X @ B[:3, 3] - A[:3, 3] for A, B in zip(A들, B들)])
    t_X = np.linalg.lstsq(왼쪽, 오른쪽, rcond=None)[0]
    return 변환(R_X, t_X)
