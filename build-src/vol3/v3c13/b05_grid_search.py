import matplotlib.pyplot as plt
import numpy as np

from 격자도구 import 해상도
from 격자탐색 import 경로_길이, 맨해튼, 옥타일, 탐색
from 지도준비 import 로봇_반지름, 막힌_칸, 부풀리기, 점들, 칸

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

막힘 = 막힌_칸()
통과 = 부풀리기(막힘, 로봇_반지름)
시작, 목표 = 칸((6.0, 1.7)), 칸((3.7, 6.7))              # 섬 아래에서 섬 위로
방법들 = [("BFS (걸음 수만 센다)", "BFS", 옥타일, 1.0), ("다익스트라", "다익스트라", 옥타일, 1.0),
        ("A* (옥타일 휴리스틱)", "A*", 옥타일, 1.0), ("A* (맨해튼 휴리스틱)", "A*", 맨해튼, 1.0),
        ("가중 A* (옥타일 × 2)", "A*", 옥타일, 2.0)]
결과 = {}
print("경로 길이  걸음 수  펼친 칸  방법")
for 이름, 방법, 휴리스틱, 가중치 in 방법들:
    결과[이름] = 탐색(통과, 시작, 목표, 방법, 휴리스틱, 가중치)
    경로, 펼침 = 결과[이름]
    print(f"{경로_길이(경로, 해상도):7.3f}m {len(경로) - 1:7d} {펼침.sum():8d}  {이름}")

그림, 칸들 = plt.subplots(1, 3, figsize=(13, 3.9))
바탕 = np.where(막힘, 0.75, np.where(~통과, 0.35, 0.0))         # 벽 / 부풀린 테두리 / 빈칸
for 그림칸, 이름 in zip(칸들, ["다익스트라", "A* (옥타일 휴리스틱)", "가중 A* (옥타일 × 2)"]):
    경로, 펼침 = 결과[이름]
    그림칸.imshow(바탕.T, origin="lower", extent=[-0.5, 10.5, -0.5, 8.5], cmap="gray_r", vmin=0, vmax=1)
    그림칸.imshow(np.ma.masked_where(~펼침, 펼침).T, origin="lower", extent=[-0.5, 10.5, -0.5, 8.5],
                cmap="autumn", alpha=0.45, vmin=0, vmax=1)            # 펼친 칸을 노랗게
    그림칸.plot(*점들(경로).T, color="tab:blue", linewidth=2)
    그림칸.plot(*점들([시작])[0], "ko", markersize=5)
    그림칸.plot(*점들([목표])[0], "k*", markersize=11)
    그림칸.set(title=f"{이름.split(' (')[0]}: 펼친 칸 {펼침.sum()}", xticks=[], yticks=[])
그림.tight_layout()
그림.savefig("grid_search.png", dpi=200)
print("저장: grid_search.png")
