import matplotlib.pyplot as plt
import numpy as np

from 내비실습 import 목적지_하나, 장애물_층
from 주행장면 import 장면_만들기
from 지도도구 import 지도_그리기, 지도_원점, 지도_크기, 해상도

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

목적지들 = {"가": (8.5, 1.8), "나": (8.5, 6.8), "다": (1.2, 6.5), "라": (1.5, 1.5)}
모델, 데이터 = 장면_만들기((1.5, 1.5, 0.0))
층 = 장애물_층(지도_그리기(모델))
기록들 = {}
print("목적지 | 도착 | 걸린 시간 | 달린 거리 | 최소 여유 | 다시 계획 | 복구 | 부딪힘")
for 이름, 목표 in 목적지들.items():
    기록 = 목적지_하나(모델, 데이터, 층, 목표)
    기록들[이름] = 기록
    거리 = np.sum(np.linalg.norm(np.diff(기록["궤적"][:, :2], axis=0), axis=1))
    print(f"{이름} {목표} | {'예' if 기록['도착'] else '아니요'} | {기록['걸린_초']:.1f}초 | {거리:.2f}m | "
          f"{기록['최소_여유']:.2f}m | {기록['다시_계획']}번 | {기록['복구']}번 | {기록['부딪힘']}번")
print(f"합계: {데이터.time:.1f}초")

범위 = [지도_원점[0], 지도_원점[0] + 지도_크기[0] * 해상도, 지도_원점[1], 지도_원점[1] + 지도_크기[1] * 해상도]
그림, 칸 = plt.subplots(figsize=(7.5, 6))
칸.imshow((층.정적 | 층.본).T * 1.0 + 층.정적.T, origin="lower", extent=범위, cmap="Greys", vmax=2.5)
for (이름, 기록), 색 in zip(기록들.items(), ["tab:blue", "tab:orange", "tab:green", "tab:purple"]):
    칸.plot(*기록["경로들"][0].T, "--", color=색, lw=1)            # 처음 계획한 경로
    칸.plot(기록["궤적"][:, 0], 기록["궤적"][:, 1], color=색, lw=2, label=f"→ {이름}")
    칸.annotate(이름, 목적지들[이름], xytext=(6, 6), textcoords="offset points", fontsize=13)
    칸.plot(*목적지들[이름], "k*", ms=12)
칸.legend(loc="center", fontsize=9)
칸.set(xlabel="x(m)", ylabel="y(m)")
그림.tight_layout()
그림.savefig("nav_run.png", dpi=200)
print("저장: nav_run.png")
