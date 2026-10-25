import matplotlib.pyplot as plt
import numpy as np

from 바퀴로봇 import 움직이기
from 바퀴장면 import 달리기, 표지들
from 실습도구 import ekf_돌리기, 오차

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

기록 = 달리기(100.0, np.random.default_rng(0))
참 = 기록["참"]
상태, 오도_경로 = np.zeros(3), []
for 이동, 회전 in 기록["오도"]:
    상태 = 움직이기(상태, 이동, 회전)
    오도_경로.append(상태)
오도_경로 = np.array(오도_경로)
ekf_경로, _ = ekf_돌리기(기록)

print("            | 위치 평균 | 위치 최대 | 위치 끝  | 방향 평균 | 방향 최대")
for 이름, 경로 in [("오도메트리만", 오도_경로), ("EKF", ekf_경로)]:
    위치, 방향 = 오차(경로, 참)
    방향_도 = np.rad2deg(np.abs(방향))
    print(f" {이름:10s} | {위치.mean():.3f}m | {위치.max():.3f}m | {위치[-1]:.3f}m | "
          f"{방향_도.mean():5.2f}도 | {방향_도.max():5.2f}도")

그림, 칸 = plt.subplots(figsize=(6, 6))
얼음 = plt.Rectangle((1.2 - 0.35, 1.2 - 0.6), 0.7, 1.2, color="lightblue", label="얼음판")
칸.add_patch(얼음)
칸.plot(참[:, 0], 참[:, 1], color="black", lw=2.5, label="참 경로")
칸.plot(오도_경로[:, 0], 오도_경로[:, 1], color="tab:orange", lw=1.2, label="오도메트리만")
칸.plot(ekf_경로[:, 0], ekf_경로[:, 1], color="tab:red", lw=1.2, ls="--", label="EKF")
칸.plot(표지들[:, 0], 표지들[:, 1], "g^", ms=12, label="표지")
칸.plot(0, 0, "ko", ms=6)
칸.set_aspect("equal")
칸.set_xlabel("x(m)")
칸.set_ylabel("y(m)")
칸.legend(fontsize=8, loc="center right")
그림.tight_layout()
그림.savefig("ekf_paths.png", dpi=200)
print("저장: ekf_paths.png")
