import time

import matplotlib.pyplot as plt
import numpy as np

from 비선형MPC import 계획
from 유니사이클 import 굴리기, 목표, 여유, 장애물, 주기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

그림, 칸 = plt.subplots(figsize=(8, 3.4))
for N in [5, 20]:
    상태 = np.array([0.0, 0.0, 0.0])
    입력들 = np.tile([0.3, 0.0], (N, 1))                  # 처음 추측: 천천히 곧장
    경로, 걸린_시간, 가장_가까이 = [상태], [], np.inf
    for 걸음 in range(150):                               # 최대 15초
        시작 = time.perf_counter()
        입력들, _ = 계획(상태, np.r_[입력들[1:], 입력들[-1:]])   # 지난 답을 한 칸 당겨 첫 추측으로
        걸린_시간.append(time.perf_counter() - 시작)
        if N == 20 and 걸음 in (0, 15, 30, 45):             # 이 순간 머릿속에 그린 2초 계획
            예측 = 굴리기(상태, 입력들)
            칸.plot(예측[:, 0], 예측[:, 1], color="tab:red", linewidth=6, alpha=0.3)
            칸.plot(*예측[-1, :2], "|", color="tab:red", markersize=12)
        상태 = 굴리기(상태, 입력들[:1])[0]                    # 첫 입력만 실제로 쓴다
        경로.append(상태)
        가장_가까이 = min(가장_가까이, 여유(상태[None]).min())
        if np.linalg.norm(상태[:2] - 목표) < 0.05:
            break
    경로 = np.array(경로)
    남은_거리 = np.linalg.norm(경로[-1, :2] - 목표)
    걸린_시간 = np.array(걸린_시간) * 1000
    print(f"N={N:2d}: {len(경로) - 1}주기 뒤 남은 거리 {남은_거리:.2f}m, "
          f"최소 여유 {round(가장_가까이 * 100, 1) + 0.0}cm | "
          f"풀이 중앙값 {np.median(걸린_시간):.1f}ms, 최대 {걸린_시간.max():.0f}ms(첫 주기 {걸린_시간[0]:.0f}ms)")
    칸.plot(경로[:, 0], 경로[:, 1], ".-", markersize=3, label=f"N={N}")
for x, y, r in 장애물:
    칸.add_patch(plt.Circle((x, y), r, color="gray"))
칸.plot(*목표, "k*", markersize=12, label="목표")
칸.plot([], [], color="tab:red", linewidth=6, alpha=0.3, label="N=20의 2초 계획")
칸.set_xlabel("x(m)")
칸.set_ylabel("y(m)")
칸.set_aspect("equal")
칸.set_xlim(-0.2, 4.4)
칸.set_ylim(-0.4, 2.1)
칸.legend(fontsize=8, loc="upper left")
그림.tight_layout()
그림.savefig("nmpc_corridor.png", dpi=200)
print("저장: nmpc_corridor.png")
