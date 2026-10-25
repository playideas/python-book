import matplotlib.pyplot as plt
import numpy as np

from 등속데이터 import 등속_모델, 시간, 주기, 참_속도, 참_위치, 측정
from 칼만도구 import 갱신, 예측

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

F, Q = 등속_모델(q=0.1)
H = np.array([[1.0, 0.0]])                       # 위치만 잰다
R = np.array([[0.1**2]])
x, P = np.array([측정[0], 0.0]), np.diag([0.1**2, 1.0])
추정, 표준편차 = [], []
for z in 측정:
    x, P = 예측(x, P, F, Q)
    x, P, _, _ = 갱신(x, P, np.array([z]), H, R)
    추정.append(x)
    표준편차.append(np.sqrt(np.diag(P)))
추정, 표준편차 = np.array(추정), np.array(표준편차)
차분_속도 = np.diff(측정, prepend=측정[0]) / 주기    # 위치 측정을 그냥 빼서 얻은 속도


def rms(a: np.ndarray) -> float:
    return float(np.sqrt(np.mean(a[10:] ** 2)))     # 처음 1초는 빼고 잰다


print(f"위치 RMS: 측정 {rms(측정 - 참_위치):.3f}m → 칼만 {rms(추정[:, 0] - 참_위치):.3f}m")
print(f"속도 RMS: 차분 {rms(차분_속도 - 참_속도):.3f}m/s → 칼만 {rms(추정[:, 1] - 참_속도):.3f}m/s")
print(f"필터가 말하는 표준편차: 위치 {표준편차[-1, 0]:.3f}m, 속도 {표준편차[-1, 1]:.3f}m/s")

그림, 칸들 = plt.subplots(1, 2, figsize=(10, 3.2))
칸들[0].plot(시간, 측정 - 참_위치, ".", ms=2, color="gray", label="측정 오차")
칸들[0].plot(시간, 추정[:, 0] - 참_위치, color="tab:red", label="칼만 오차")
칸들[0].fill_between(시간, -2 * 표준편차[:, 0], 2 * 표준편차[:, 0], color="tab:red", alpha=0.15, label="±2σ")
칸들[0].set_ylabel("위치 오차(m)")
칸들[1].plot(시간, 차분_속도, color="gray", lw=0.6, label="측정 차분")
칸들[1].plot(시간, 참_속도, color="black", lw=2, label="참 속도")
칸들[1].plot(시간, 추정[:, 1], color="tab:red", label="칼만 추정")
칸들[1].set_ylim(-1, 2)
칸들[1].set_ylabel("속도(m/s)")
for 칸 in 칸들:
    칸.set_xlabel("시간(초)")
    칸.legend(fontsize=8, loc="upper right")
그림.tight_layout()
그림.savefig("cv_track.png", dpi=200)
print("저장: cv_track.png")
