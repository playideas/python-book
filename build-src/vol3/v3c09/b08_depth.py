import matplotlib.pyplot as plt
import mujoco
import numpy as np

from 비전장면 import K_만들기, T_세계_카메라, 머리_fovy, 장면_xml, 찍기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

모델 = mujoco.MjModel.from_xml_string(장면_xml())
데이터 = mujoco.MjData(모델)
컬러, 깊이 = 찍기(모델, 데이터, "머리")
K = K_만들기(머리_fovy)
T = T_세계_카메라(데이터, "머리")

# 탁자 윗면(높이 0.75m) 위의 픽셀 몇 개: 광선이 탁자 면과 만나는 점을 직접 계산해 비교한다
for u, v in [(320, 240), (40, 420), (560, 330)]:
    광선_카메라 = np.linalg.inv(K) @ [u, v, 1.0]               # z 성분이 1인 방향
    광선_세계 = T[:3, :3] @ 광선_카메라
    s = (0.75 - T[2, 3]) / 광선_세계[2]                         # 광선이 높이 0.75m에 닿는 곳까지의 배수
    print(f"픽셀 ({u:3d},{v:3d}): 깊이 영상 {깊이[v, u]:.4f}m | 광선의 z 성분 {s:.4f}m"
          f" | 카메라에서 곧은 거리 {s * np.linalg.norm(광선_카메라):.4f}m")

그림, 칸들 = plt.subplots(1, 2, figsize=(9, 3.4))
칸들[0].imshow(컬러)
칸들[0].set_title("컬러 사진", fontsize=10)
면 = 칸들[1].imshow(np.where(깊이 < 3, 깊이, np.nan), cmap="viridis")
칸들[1].set_title("깊이 영상(m)", fontsize=10)
그림.colorbar(면, ax=칸들[1], fraction=0.035)
for 칸 in 칸들:
    칸.axis("off")
그림.tight_layout()
그림.savefig("depth.png", dpi=200)
print("저장: depth.png")
