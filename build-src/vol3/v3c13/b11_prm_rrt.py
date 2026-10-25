import matplotlib.pyplot as plt
import numpy as np

from 팔공간 import 관절공간_지도, 상한, 선분_충돌, 충돌, 하한
from 표본계획 import PRM, RRT, 경로_길이

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

시작, 목표 = np.deg2rad([-20.0, 40.0]), np.deg2rad([85.0, 30.0])     # 13.1절 그림의 자세 가, 나
print(f"곧게 이으면 부딪히는가? {선분_충돌(시작, 목표)}, 곧은 거리 {np.linalg.norm(목표 - 시작):.3f}rad")

경로_PRM, 점_PRM, 간선_PRM = PRM(시작, 목표, 충돌, 선분_충돌, 하한, 상한, np.random.default_rng(0))
print(f"PRM : 점 {len(점_PRM)}개, 간선 {sum(map(len, 간선_PRM.values())) // 2}개, 경로 {경로_길이(경로_PRM):.3f}rad")
경로_RRT, 점_RRT, 부모_RRT, 반복 = RRT(시작, 목표, 선분_충돌, 하한, 상한, np.random.default_rng(0))
print(f"RRT : {반복}번 뽑아 나무 점 {len(점_RRT)}개, 경로 {경로_길이(경로_RRT):.3f}rad")
경로_별, 점_별, 부모_별, 기록 = RRT(시작, 목표, 선분_충돌, 하한, 상한, np.random.default_rng(0),
                                최대_반복=3000, 별=True)
print("RRT*: 가장 좋은 경로 " + ", ".join(f"{n}번째 {기록[n - 1]:.3f}" for n in [500, 1000, 2000, 3000]) + "rad")

막힘 = 관절공간_지도()
그림, 칸들 = plt.subplots(1, 3, figsize=(13, 4.4))
for 그림칸, 제목, 경로 in zip(칸들, ["PRM (길 지도)", "RRT", "RRT* (3000번)"], [경로_PRM, 경로_RRT, 경로_별]):
    그림칸.imshow(막힘.T, origin="lower", extent=[-180, 180, -180, 180], cmap="gray_r", vmin=0, vmax=1.6)
    그림칸.set(title=f"{제목}: {경로_길이(경로):.2f}rad", xlabel="어깨 (도)", ylabel="팔꿈치 (도)")
잇기들 = [(칸들[0], 점_PRM, [(i, j) for i, 이웃 in 간선_PRM.items() for j, _ in 이웃 if i < j]),
         (칸들[1], 점_RRT, [(p, k) for k, p in enumerate(부모_RRT) if p is not None]),
         (칸들[2], 점_별, [(p, k) for k, p in enumerate(부모_별) if p is not None])]
for 그림칸, 점들, 짝들 in 잇기들:                    # 길 지도의 간선, 나무의 가지
    for i, j in 짝들:
        그림칸.plot(*np.rad2deg(점들[[i, j]]).T, color="tab:cyan", linewidth=0.4)
for 그림칸, 경로 in zip(칸들, [경로_PRM, 경로_RRT, 경로_별]):
    그림칸.plot(*np.rad2deg(경로).T, color="tab:red", linewidth=2)
    그림칸.plot(*np.rad2deg(시작), "ko")
    그림칸.plot(*np.rad2deg(목표), "*", color="gold", markeredgecolor="k", markersize=13)
그림.tight_layout()
그림.savefig("sampling.png", dpi=200)
print("저장: sampling.png")
