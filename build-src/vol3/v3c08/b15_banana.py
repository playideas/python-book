import matplotlib.pyplot as plt
import numpy as np

from 바퀴로봇 import 움직이기, 움직임_야코비안

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# 방향을 잘 모르는(표준편차 30도) 로봇이 앞으로 1m 간다
평균 = np.zeros(3)
P = np.diag([0.02**2, 0.02**2, np.deg2rad(30) ** 2])

# (1) 점 5000개를 뽑아 하나하나 옮긴다(파티클 필터의 방식). 실제 분포를 보여 준다
옮긴_점 = np.array([움직이기(p, 1.0, 0.0) for p in np.random.default_rng(0).multivariate_normal(평균, P, 5000)])

# (2) EKF: 평균은 그대로 옮기고, 공분산은 야코비안으로 옮긴다
F, _ = 움직임_야코비안(평균, 1.0, 0.0)
ekf = (움직이기(평균, 1.0, 0.0)[:2], (F @ P @ F.T)[:2, :2])

# (3) UKF의 방식: 대표 점(시그마 점) 7개만 옮긴 뒤 평균과 공분산을 다시 잰다
L = np.linalg.cholesky(3 * P)
시그마 = np.array([움직이기(평균 + 부호 * L[:, i], 1.0, 0.0) for 부호 in [1, -1] for i in range(3)])[:, :2]
ukf = (시그마.mean(axis=0), np.cov(시그마.T, bias=True))     # 가운데 점의 가중치는 0으로 둔 경우

그림, 칸 = plt.subplots(figsize=(6.4, 4))
칸.scatter(옮긴_점[:, 0], 옮긴_점[:, 1], s=1, color="gray", alpha=0.3, label="점 5000개(실제 분포)")
print("             | 평균 x  | x 표준편차 | y 표준편차")
for 이름, (m, C), 색 in [("점 5000개", (옮긴_점[:, :2].mean(axis=0), np.cov(옮긴_점[:, :2].T)), None),
                       ("EKF", ekf, "tab:blue"), ("시그마 점", ukf, "tab:red")]:
    print(f" {이름:10s} | {m[0]:.3f}m | {np.sqrt(C[0, 0]):.3f}m   | {np.sqrt(C[1, 1]):.3f}m")
    if 색:
        값, 벡터 = np.linalg.eigh(C)
        각 = np.linspace(0, 2 * np.pi, 100)
        점 = 벡터 @ (2 * np.sqrt(값)[:, None] * np.array([np.cos(각), np.sin(각)]))
        칸.plot(m[0] + 점[0], m[1] + 점[1], color=색, label=f"{이름}(2σ)")
        칸.plot(m[0], m[1], "o", color=색)
칸.plot(시그마[:, 0], 시그마[:, 1], "x", color="tab:red", ms=8, label="옮긴 시그마 점")
칸.set_aspect("equal")
칸.set_xlabel("x(m)")
칸.set_ylabel("y(m)")
칸.legend(fontsize=8, loc="upper left", bbox_to_anchor=(1.02, 1))
그림.tight_layout()
그림.savefig("banana.png", dpi=200)
print("저장: banana.png")
