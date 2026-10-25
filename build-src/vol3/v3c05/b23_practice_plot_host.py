# 맥(호스트)에서 실행: 컨테이너가 남긴 CSV를 읽어 그린다
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

목표 = np.array([2.0, 1.0])
주기 = 0.1
그림, (왼쪽, 오른쪽) = plt.subplots(1, 2, figsize=(9.5, 3.8))
for 이득, 색 in [("0.5", "tab:green"), ("1.5", "tab:blue"), ("12.0", "tab:red")]:
    경로 = np.loadtxt(f"path_gain_{이득}.csv", delimiter=",", skiprows=1)    # 첫 줄은 열 이름
    거리 = np.linalg.norm(경로 - 목표, axis=1)
    시간 = np.arange(len(경로)) * 주기
    왼쪽.plot(경로[:, 0], 경로[:, 1], "o-", markersize=2, color=색, label=f"이득 {이득}")
    오른쪽.plot(시간, 거리, color=색, label=f"이득 {이득}")
    print(f"이득 {이득:>4s}: 8초 뒤 남은 거리 {거리[-1]:.3f}m, 마지막 2초 평균 {거리[-20:].mean():.3f}m, "
          f"가장 멀 때 {거리[-20:].max():.3f}m")
왼쪽.scatter(*목표, marker="*", s=250, color="gold", edgecolors="black", zorder=5, label="목표")
왼쪽.set_xlim(1.7, 2.1)                          # 목표 근처만 크게 본다
왼쪽.set_ylim(0.85, 1.1)
왼쪽.set_xlabel("x (m)")
왼쪽.set_ylabel("y (m)")
왼쪽.set_aspect("equal")
왼쪽.set_title("목표 근처의 경로")
왼쪽.legend(loc="lower right", fontsize=8)
오른쪽.set_ylim(0, 0.5)
오른쪽.set_xlabel("시간(초)")
오른쪽.set_ylabel("목표까지 남은 거리(m)")
오른쪽.set_title("남은 거리")
오른쪽.legend(fontsize=8)
그림.tight_layout()
그림.savefig("ros_point_robot.png", dpi=200)
print("저장: ros_point_robot.png")
