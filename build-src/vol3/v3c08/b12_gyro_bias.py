import matplotlib.pyplot as plt
import numpy as np

from 칼만도구 import 갱신, 예측
from 흔들판 import rms_도, 가속도_피치, 기록하기, 센서_더하기, 주기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

기록 = 기록하기()
자이로, 가속도 = 센서_더하기(기록, np.random.default_rng(0))
가속도_피치값 = 가속도_피치(가속도)
참값, 시간 = 기록["참_피치"], 기록["시간"]

# 상태 x = [피치, 자이로 치우침]. 입력 u = 자이로 값. 피치 += (자이로 - 치우침) × 주기
F = np.array([[1.0, -주기], [0.0, 1.0]])
B = np.array([[주기], [0.0]])
Q = np.diag([(0.01 * 주기) ** 2, (0.0002) ** 2])    # 자이로 잡음이 쌓이는 정도, 치우침이 천천히 변하는 정도
H = np.array([[1.0, 0.0]])                            # 가속도계는 피치만 잰다
R = np.array([[(0.5 / 9.81) ** 2]])                   # 8.1절: 가속도 잡음 0.5m/s² ≈ 피치 잡음 0.05rad

x, P = np.array([가속도_피치값[0], 0.0]), np.diag([0.1**2, 0.05**2])
추정, 치우침_표준편차 = [], []
for w, a in zip(자이로, 가속도_피치값):
    x, P = 예측(x, P, F, Q, B, np.array([w]))
    K = P @ H.T / (H @ P @ H.T + R)
    x, P, _, _ = 갱신(x, P, np.array([a]), H, R)
    추정.append(x)
    치우침_표준편차.append(np.sqrt(P[1, 1]))
추정 = np.array(추정)

# 비교: 8.2절의 상보 필터(알파 0.98)
피치, 상보 = 가속도_피치값[0], []
for w, a in zip(자이로, 가속도_피치값):
    피치 = 0.98 * (피치 + w * 주기) + 0.02 * a
    상보.append(피치)
상보 = np.array(상보)

뒤쪽 = 시간 >= 5                                       # 처음 5초는 빼고 비교
for 이름, 값 in [("상보 필터", 상보), ("칼만(치우침 포함)", 추정[:, 0])]:
    오차 = 값 - 참값
    print(f"{이름:10s}: 오차 RMS {rms_도(오차[뒤쪽]):.2f}도, 평균 오차 {np.rad2deg(오차[뒤쪽].mean()):+.2f}도")
print(f"추정한 치우침: {추정[-1, 1]:.4f}rad/s (참값 0.0200), 표준편차 {치우침_표준편차[-1]:.4f}")
print(f"끝의 칼만 이득: 피치 {K[0, 0]:.4f}, 치우침 {K[1, 0]:.4f}")

그림, 칸들 = plt.subplots(1, 2, figsize=(10, 3.2))
칸들[0].plot(시간, np.rad2deg(상보 - 참값), color="tab:blue", lw=0.8, label="상보 필터")
칸들[0].plot(시간, np.rad2deg(추정[:, 0] - 참값), color="tab:red", lw=0.8, label="칼만(치우침 포함)")
칸들[0].set_ylim(-5, 5)
칸들[0].set_ylabel("피치 오차(도)")
칸들[1].plot(시간, 추정[:, 1], color="tab:red", label="추정한 치우침")
칸들[1].fill_between(시간, 추정[:, 1] - 2 * np.array(치우침_표준편차), 추정[:, 1] + 2 * np.array(치우침_표준편차),
                   color="tab:red", alpha=0.15, label="±2σ")
칸들[1].axhline(0.02, color="black", ls="--", label="참 치우침 0.02")
칸들[1].set_ylabel("자이로 치우침(rad/s)")
for 칸 in 칸들:
    칸.set_xlabel("시간(초)")
    칸.legend(fontsize=8, loc="lower right")
그림.tight_layout()
그림.savefig("gyro_bias_kf.png", dpi=200)
print("저장: gyro_bias_kf.png")
