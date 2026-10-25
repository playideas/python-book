import matplotlib.pyplot as plt
import numpy as np

from 포즈그래프 import 그래프_펴기
from 포즈도구 import 포즈_잇기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# 한 변 2m인 네모를 1m씩 8걸음에 한 바퀴: 두 걸음마다 왼쪽으로 90도
참_증분들 = [np.array([1.0, 0.0, 0.0]), np.array([1.0, 0.0, np.pi / 2])] * 4
잰_증분들 = [z + [0.0, 0.0, np.deg2rad(3)] for z in 참_증분들]    # 바퀴가 걸음마다 3도씩 더 돌았다고 잰다

참_포즈들, 처음_포즈들 = [np.zeros(3)], [np.zeros(3)]
for 참, 잰 in zip(참_증분들, 잰_증분들):
    참_포즈들.append(포즈_잇기(참_포즈들[-1], 참))
    처음_포즈들.append(포즈_잇기(처음_포즈들[-1], 잰))
참_포즈들, 처음_포즈들 = np.array(참_포즈들), np.array(처음_포즈들)

간선들 = [(i, i + 1, 잰_증분들[i]) for i in range(8)]       # 오도메트리 간선 8개
간선들.append((0, 8, np.zeros(3)))                          # 루프 닫기: "8번은 0번과 같은 자리다"

펴진_포즈들 = 그래프_펴기(처음_포즈들, 간선들)
for 이름, 포즈들 in [("오도메트리만", 처음_포즈들), ("그래프 편 뒤", 펴진_포즈들)]:
    오차 = np.linalg.norm(포즈들[:, :2] - 참_포즈들[:, :2], axis=1)
    print(f"{이름}: 8번 포즈 {np.round(포즈들[8, :2], 3) + 0.0}, 포즈 오차 평균 {오차.mean():.3f}m, 가장 큰 {오차.max():.3f}m")
print("포즈마다 옮겨진 거리:", np.round(np.linalg.norm(펴진_포즈들[:, :2] - 처음_포즈들[:, :2], axis=1), 2))

그림, 칸 = plt.subplots(figsize=(4.6, 4.2))
for 포즈들, 모양, 이름 in [(참_포즈들, "k-o", "참"), (처음_포즈들, "--s", "오도메트리만"), (펴진_포즈들, "-^", "그래프 편 뒤")]:
    칸.plot(포즈들[:, 0], 포즈들[:, 1], 모양, ms=5, label=이름)
칸.plot([처음_포즈들[8, 0], 0], [처음_포즈들[8, 1], 0], ":", color="tab:red", label="루프 닫기 간선")
칸.set_aspect("equal")
칸.set_xlabel("x (m)")
칸.set_ylabel("y (m)")
칸.legend(fontsize=8, loc="center")
그림.tight_layout()
그림.savefig("posegraph_tiny.png", dpi=200)
print("저장: posegraph_tiny.png")
