import matplotlib.pyplot as plt
import numpy as np

from 두링크 import 야코비안2
from 시간매기기 import 안전한_스플라인
from 팔공간 import 관절_점들, 상한, 선분_충돌, 여유, 장애물들, 하한
from 표본계획 import RRT, 지름길

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

시작, 목표 = np.deg2rad([-20.0, 40.0]), np.deg2rad([85.0, 30.0])
날것, _, _, _ = RRT(시작, 목표, 선분_충돌, 하한, 상한, np.random.default_rng(0))
곡선, _ = 안전한_스플라인(지름길(날것, 선분_충돌, np.random.default_rng(1)),
                       lambda 점들: bool((여유(점들) < 0).any()))

팔꿈치들, 손끝들 = 관절_점들(곡선)                     # 3장 순기구학: 관절 경로 → 손끝 경로
행렬식 = np.array([np.linalg.det(야코비안2(q)) for q in 곡선])
print(f"손끝이 지나간 길 {np.linalg.norm(np.diff(손끝들, axis=0), axis=1).sum():.3f}m "
      f"(시작과 끝 손끝 사이 곧은 거리 {np.linalg.norm(손끝들[-1] - 손끝들[0]):.3f}m)")
print(f"손끝이 받침에서 가장 가까울 때 {np.linalg.norm(손끝들, axis=1).min():.3f}m")
print(f"야코비안 행렬식: 가장 작을 때 {np.abs(행렬식).min():.4f} (팔꿈치 {np.rad2deg(곡선[np.abs(행렬식).argmin(), 1]):.1f}도)")

그림, 칸 = plt.subplots(figsize=(5.4, 5))
for x, y, r in 장애물들:
    칸.add_patch(plt.Circle((x, y), r, color="dimgray"))
for k in np.linspace(0, len(곡선) - 1, 9).astype(int):       # 경로 위 아홉 순간의 팔 모양
    선 = np.array([[0, 0], 팔꿈치들[k], 손끝들[k]])
    칸.plot(*선.T, "o-", color=plt.cm.viridis(k / len(곡선)), linewidth=2, markersize=3)
칸.plot(*손끝들.T, color="tab:red", linewidth=1.5, label="손끝 경로")
칸.set(xlim=(-0.8, 0.8), ylim=(-0.6, 0.8), aspect="equal", xlabel="x (m)", ylabel="y (m)")
칸.legend(fontsize=8, loc="lower left")
그림.tight_layout()
그림.savefig("fk_path.png", dpi=200)
print("저장: fk_path.png")
