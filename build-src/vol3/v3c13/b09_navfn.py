import matplotlib.pyplot as plt
import numpy as np

from 격자탐색 import 갈_수_있는_이웃, 탐색
from 디귿장면 import 규칙_달리기, 목표, 벽들, 벽까지, 시작
from 점로봇 import 속도_제한
from 퍼텐셜 import 내리막, 퍼텐셜

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# ㄷ자 장면을 5cm 칸 격자로 옮기고, 벽에서 0.15m 안쪽 칸은 막는다(점 로봇에 여유를 준 것)
해상도, 원점 = 0.05, np.array([-0.5, -0.5])
X, Y = np.meshgrid(원점[0] + (np.arange(80) + 0.5) * 해상도, 원점[1] + (np.arange(60) + 0.5) * 해상도,
                   indexing="ij")
통과 = np.vectorize(lambda x, y: 벽까지(np.array([x, y]))[0] > 0.15)(X, Y)


def 칸(점) -> tuple[int, int]:
    return tuple(int(v) for v in np.floor((np.asarray(점) - 원점) / 해상도))


남은, _ = 탐색(통과, 칸(목표), None, "다익스트라")       # 목표에서 끝까지 펼친 '남은 거리'가 새 높이
현재, 길 = 칸(시작), [칸(시작)]
while 남은[현재] > 0:                                  # 이웃 중 남은 거리가 가장 작은 칸으로 내려간다
    현재 = min((다음 for 다음, _ in 갈_수_있는_이웃(통과, 현재)), key=lambda c: 남은[c])
    길.append(현재)
길_점 = 원점 + (np.array(길) + 0.5) * 해상도
print(f"거리장 따라 내려가기: {len(길) - 1}걸음 만에 목표 칸 도착, "
      f"길이 {np.linalg.norm(np.diff(길_점, axis=0), axis=1).sum():.3f}m")
print(f"시작 칸의 '남은 거리' {남은[칸(시작)] * 해상도:.3f}m")

위치, 퍼텐셜_길 = 시작.copy(), [시작.copy()]
for _ in range(6000):
    위치 = 위치 + 속도_제한(내리막(위치)) * 0.01
    퍼텐셜_길.append(위치)
퍼텐셜_길, 규칙_길 = np.array(퍼텐셜_길), 규칙_달리기()

그림, (왼쪽, 오른쪽) = plt.subplots(1, 2, figsize=(10, 4))
높이 = np.vectorize(lambda x, y: 퍼텐셜(np.array([x, y])))(X, Y)
왼쪽.contour(X, Y, np.minimum(높이, 4), levels=25, cmap="viridis", linewidths=0.7)
왼쪽.plot(*규칙_길.T, color="tab:orange", label="1장 규칙")
왼쪽.plot(*퍼텐셜_길.T, "--", color="tab:red", label="퍼텐셜 내리막")
왼쪽.set_title("퍼텐셜 필드: 우묵한 곳에 갇힌다")
오른쪽.imshow(np.where(통과, 남은 * 해상도, np.nan).T, origin="lower", extent=[-0.5, 3.5, -0.5, 2.5])
오른쪽.plot(*길_점.T, color="white", linewidth=2, label="거리장 내리막")
오른쪽.set_title("목표에서 잰 거리장: 어디서든 목표로 내려간다")
for 그림칸 in (왼쪽, 오른쪽):
    for x0, x1, y0, y1 in 벽들:
        그림칸.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, color="dimgray"))
    그림칸.plot(*시작, "ko")
    그림칸.plot(*목표, "*", color="gold", markeredgecolor="k", markersize=14)
    그림칸.set_xlim(-0.5, 3.5)
    그림칸.set_ylim(-0.5, 2.5)
    그림칸.set_aspect("equal")
    그림칸.legend(fontsize=8, loc="lower left")
그림.tight_layout()
그림.savefig("potential.png", dpi=200)
print("저장: potential.png")
