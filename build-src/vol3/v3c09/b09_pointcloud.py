import matplotlib.pyplot as plt
import mujoco
import numpy as np

from 비전장면 import K_만들기, T_세계_카메라, 머리_fovy, 장면_xml, 찍기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def 점구름(깊이: np.ndarray, K: np.ndarray) -> np.ndarray:
    """깊이 영상의 모든 픽셀을 한꺼번에 역투영한다. (높이, 너비, 3) 카메라 광학 좌표."""
    v, u = np.indices(깊이.shape)
    X = (u - K[0, 2]) / K[0, 0] * 깊이
    Y = (v - K[1, 2]) / K[1, 1] * 깊이
    return np.stack([X, Y, 깊이], axis=-1)


모델 = mujoco.MjModel.from_xml_string(장면_xml())
데이터 = mujoco.MjData(모델)
컬러, 깊이 = 찍기(모델, 데이터, "머리")
점_카메라 = 점구름(깊이, K_만들기(머리_fovy))
T = T_세계_카메라(데이터, "머리")
점_세계 = 점_카메라.reshape(-1, 3) @ T[:3, :3].T + T[:3, 3]      # 모든 점에 T를 한 번에 적용
색 = 컬러.reshape(-1, 3) / 255
가까운 = 깊이.ravel() < 3                                       # 하늘(아무것도 없는 곳)은 뺀다
print("점 개수:", 가까운.sum())

탁자_위 = 가까운 & (np.abs(점_세계[:, 0] - 0.55) < 0.3) & (np.abs(점_세계[:, 1]) < 0.4)
높이들 = 점_세계[탁자_위, 2]
print(f"탁자 영역 점의 높이: 중앙값 {np.median(높이들):.4f}m, 가장 높은 점 {높이들.max():.3f}m")

상자_안 = 가까운 & np.all((점_세계 > [0.1, -0.5, 0.6]) & (점_세계 < [1.0, 0.5, 0.95]), axis=1)
고른 = np.flatnonzero(상자_안)[::5]                             # 그림이 무겁지 않게 다섯 개에 하나만
그림 = plt.figure(figsize=(6, 4.5))
칸 = 그림.add_subplot(projection="3d")
칸.scatter(*점_세계[고른].T, c=색[고른], s=0.5)
칸.set_xlabel("x (m)")
칸.set_ylabel("y (m)")
칸.set_zlabel("z (m)")
칸.set_box_aspect((0.9, 1.0, 0.35))
칸.view_init(elev=30, azim=-150)
그림.tight_layout()
그림.savefig("pointcloud.png", dpi=200)
print("저장: pointcloud.png")
