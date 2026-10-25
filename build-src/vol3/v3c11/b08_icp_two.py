import matplotlib.pyplot as plt
import numpy as np

from 정합도구 import icp
from 주행데이터 import 주행_기록
from 포즈도구 import 상대_포즈, 점_옮기기, 행렬_포즈

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

참_포즈들, 바퀴_증분들, 스캔들 = 주행_기록()
기준, 원본 = 스캔들[0], 스캔들[3]                      # 0.75m 떨어진 '이전'과 '지금' 스캔
print("정답 상대 포즈:", np.round(상대_포즈(참_포즈들[0], 참_포즈들[3]), 3) + 0.0)

T, 기록 = icp(원본, 기준)                              # 처음 추측: 움직이지 않았다(단위 행렬)
for k in [0, 5, 10, 15, 20, len(기록) - 1]:
    print(f"반복 {k + 1:2d}: 짝 사이 평균 거리 {기록[k]:.4f}m")
x, y, 각 = 행렬_포즈(T)
print(f"ICP가 찾은 것: x {x:.3f}m, y {y:.3f}m, 각 {np.rad2deg(각):.2f}도")

그림, 칸들 = plt.subplots(1, 3, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1, 1, 0.8]})
for 칸, 점들, 제목 in [(칸들[0], 원본, "맞추기 전"), (칸들[1], 점_옮기기(T, 원본), f"ICP {len(기록)}번 반복 뒤")]:
    칸.scatter(기준[:, 0], 기준[:, 1], s=5, color="tab:blue", label="이전 스캔(기준)")
    칸.scatter(점들[:, 0], 점들[:, 1], s=5, color="tab:red", label="지금 스캔")
    칸.set_title(제목)
    칸.set_aspect("equal")
칸들[0].legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2, fontsize=8)
칸들[2].plot(range(1, len(기록) + 1), 기록, "o-", ms=3)
칸들[2].set_xlabel("반복")
칸들[2].set_ylabel("짝 사이 평균 거리 (m)")
그림.tight_layout()
그림.savefig("icp.png", dpi=200)
print("저장: icp.png")
