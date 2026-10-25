import matplotlib.pyplot as plt
import numpy as np

from 바퀴로봇 import ekf_갱신, ekf_예측, 움직이기, 표지_R, 표지_보기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def 타원(칸, 평균: np.ndarray, P: np.ndarray, 색: str, 이름: str | None = None) -> None:
    """위치 공분산 P[:2, :2]의 2σ 타원을 그린다."""
    값, 벡터 = np.linalg.eigh(P[:2, :2])
    각 = np.linspace(0, 2 * np.pi, 100)
    점 = 벡터 @ (2 * np.sqrt(값)[:, None] * np.array([np.cos(각), np.sin(각)]))
    칸.plot(평균[0] + 점[0], 평균[1] + 점[1], color=색, label=이름)


생성기 = np.random.default_rng(0)
참 = np.array([0.0, 0.0, 0.0])
x, P = 참.copy(), np.diag([0.01**2, 0.01**2, np.deg2rad(1) ** 2])
그림, 칸 = plt.subplots(figsize=(6, 4))
참_경로 = [참]
for k in range(1, 51):                                # 0.1초마다 오도메트리, 5초 동안
    이동, 회전 = 0.06, 0.012
    참 = 움직이기(참, 이동 * 생성기.normal(1, 0.05), 회전 + 생성기.normal(0, 0.004))
    참_경로.append(참)
    x, P = ekf_예측(x, P, 이동, 회전)
    if k % 10 == 0:
        타원(칸, x, P, "tab:blue", "예측만 했을 때(2σ)" if k == 10 else None)
print(f"5초 예측 뒤: 위치 표준편차 축 {np.round(np.sqrt(np.linalg.eigvalsh(P[:2, :2])), 3)}m, "
      f"방향 표준편차 {np.rad2deg(np.sqrt(P[2, 2])):.2f}도, 실제 오차 {np.linalg.norm(x[:2] - 참[:2]):.3f}m")

표지 = np.array([3.5, 2.0])
z = 표지_보기(참, 표지) + 생성기.normal(0, np.sqrt(np.diag(표지_R)))
x, P, 혁신, _ = ekf_갱신(x, P, z, 표지, 표지_R)
타원(칸, x, P, "tab:red", "표지 한 번 본 뒤(2σ)")
print(f"혁신: 거리 {혁신[0]:+.3f}m, 방향 {np.rad2deg(혁신[1]):+.2f}도")
print(f"갱신 뒤:   위치 표준편차 축 {np.round(np.sqrt(np.linalg.eigvalsh(P[:2, :2])), 3)}m, "
      f"방향 표준편차 {np.rad2deg(np.sqrt(P[2, 2])):.2f}도, 실제 오차 {np.linalg.norm(x[:2] - 참[:2]):.3f}m")

칸.plot(*np.array(참_경로)[:, :2].T, color="black", lw=1, label="참 경로")
칸.plot(*표지, "k^", ms=10, label="표지")
칸.plot([참[0], 표지[0]], [참[1], 표지[1]], "k:", lw=0.8)
칸.set_aspect("equal")
칸.set_xlabel("x(m)")
칸.set_ylabel("y(m)")
칸.legend(fontsize=8, loc="upper left")
그림.tight_layout()
그림.savefig("ekf_ellipse.png", dpi=200)
print("저장: ekf_ellipse.png")
