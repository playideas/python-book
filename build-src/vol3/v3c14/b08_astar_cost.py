import matplotlib.pyplot as plt
import numpy as np

from 주행장면 import 장면_만들기
from 지도도구 import a_star, 비용_지도, 장애물까지, 지도_그리기, 지도_원점, 지도_크기, 해상도

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

모델, _ = 장면_만들기()
찬칸 = 지도_그리기(모델)
비용 = 비용_지도(찬칸)
범위 = [지도_원점[0], 지도_원점[0] + 지도_크기[0] * 해상도, 지도_원점[1], 지도_원점[1] + 지도_크기[1] * 해상도]
그림, 칸 = plt.subplots(figsize=(6.4, 5))
칸.imshow(비용.T, origin="lower", extent=범위, cmap="Greys", vmax=300)
for 목표 in [(1.2, 6.5), (8.0, 6.5)]:
    for 무게, 색 in [(0.0, "tab:red"), (3.0, "tab:blue")]:
        경로 = a_star(비용, (1.5, 1.5), 목표, 비용_무게=무게)
        길이 = np.sum(np.linalg.norm(np.diff(경로, axis=0), axis=1))
        여유 = 장애물까지(찬칸, 경로)
        print(f"목표 {목표}, 비용 무게 {무게:.0f}: 길이 {길이:.2f}m, "
              f"장애물까지 최소 {여유.min():.2f}m, 평균 {여유.mean():.2f}m")
        칸.plot(경로[:, 0], 경로[:, 1], color=색, lw=1.8, label=f"비용 무게 {무게:.0f}" if 목표[0] < 2 else None)
    칸.plot(*목표, "k*", ms=12)
칸.plot(1.5, 1.5, "ko", ms=7)
칸.legend(loc="center", fontsize=9)
칸.set(xlabel="x(m)", ylabel="y(m)")
그림.tight_layout()
그림.savefig("astar_cost.png", dpi=200)
print("저장: astar_cost.png")
