import numpy as np

from 회전도구 import Rz, 깔끔


def 변환(R: np.ndarray, p) -> np.ndarray:
    """회전 R과 이동 p를 4×4 동차 변환 하나로."""
    T = np.eye(4)
    T[:3, :3], T[:3, 3] = R, p
    return T


def 역변환(T: np.ndarray) -> np.ndarray:
    """T의 역: 회전은 전치, 이동은 -Rᵀp."""
    R, p = T[:3, :3], T[:3, 3]
    return 변환(R.T, -R.T @ p)


T_방_로봇 = 변환(Rz(90), [2.0, 1.0, 0.0])                # 방에서 본 로봇
T_로봇_컵 = 변환(np.eye(3), [0.5, 0.0, 0.8])             # 로봇에서 본 컵
T_방_컵 = T_방_로봇 @ T_로봇_컵                           # 기준 이름이 사슬처럼 이어진다
print("방에서 본 컵의 위치:", 깔끔(T_방_컵[:3, 3]))
print("점 변환(끝에 1)    :", 깔끔((T_방_로봇 @ [0.5, 0.0, 0.8, 1.0])[:3]))
print("방향 변환(끝에 0)  :", 깔끔((T_방_로봇 @ [1.0, 0.0, 0.0, 0.0])[:3]))
print("역변환 공식 == inv :", np.allclose(역변환(T_방_로봇), np.linalg.inv(T_방_로봇)))
