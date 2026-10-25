import matplotlib.pyplot as plt
import numpy as np

from 바퀴로봇 import 각도_감싸기
from 바퀴장면 import 달리기
from 실습도구 import ekf_돌리기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

기록 = 달리기(100.0, np.random.default_rng(0))
참, 시간 = 기록["참"], np.array(기록["시간"])
추정, 공분산 = ekf_돌리기(기록)
오차 = 추정 - 참
오차[:, 2] = 각도_감싸기(오차[:, 2])
표준편차 = np.sqrt(np.diagonal(공분산, axis1=1, axis2=2))

nees = np.array([e @ np.linalg.solve(P, e) for e, P in zip(오차, 공분산)])   # 오차를 P로 잰 크기
for i, 이름 in enumerate(["x", "y", "방향"]):
    print(f"{이름}: 오차가 ±2σ 안에 든 비율 {np.mean(np.abs(오차[:, i]) < 2 * 표준편차[:, i]):.1%}")
print(f"NEES 평균 {nees.mean():.2f} (상태가 3개이니 3 근처면 정직하다), 20초 이후만 보면 {nees[시간 > 20].mean():.2f}")

그림, 칸들 = plt.subplots(3, 1, figsize=(8, 5.5), sharex=True)
for 칸, i, 이름, 배율 in zip(칸들, range(3), ["x 오차(m)", "y 오차(m)", "방향 오차(도)"], [1, 1, 180 / np.pi]):
    칸.plot(시간, 오차[:, i] * 배율, color="tab:red", lw=1)
    칸.fill_between(시간, -2 * 표준편차[:, i] * 배율, 2 * 표준편차[:, i] * 배율, color="gray", alpha=0.25)
    칸.set_ylabel(이름)
칸들[0].set_title("EKF 오차(빨강)와 필터가 말하는 ±2σ(회색)", fontsize=10)
칸들[-1].set_xlabel("시간(초)")
그림.tight_layout()
그림.savefig("ekf_consistency.png", dpi=200)
print("저장: ekf_consistency.png")
