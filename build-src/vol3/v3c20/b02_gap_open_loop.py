import matplotlib.pyplot as plt
import numpy as np

from 현실팔 import 시뮬_물성, 실행, 현실_물성

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def 들뜸(t: float, q: np.ndarray) -> np.ndarray:
    """제어 없이 정해 둔 토크만 보낸다(열린 고리). 빠르기가 다른 사인파 둘을 섞었다."""
    return np.array([3.0 * np.sin(2 * np.pi * 0.7 * t) + 2.0 * np.sin(2 * np.pi * 1.9 * t),
                     1.2 * np.sin(2 * np.pi * 1.1 * t) + 0.8 * np.sin(2 * np.pi * 2.7 * t)])


시뮬 = 실행(들뜸, 6.0, 시뮬_물성)
현실 = 실행(들뜸, 6.0, 현실_물성, 시드=1)
차이_도 = np.rad2deg(현실["잰_각도"] - 시뮬["잰_각도"])
for i, 관절 in enumerate(["어깨", "팔꿈치"]):
    print(f"{관절}: 차이 RMS {np.sqrt(np.mean(차이_도[:, i] ** 2)):5.2f}도, 가장 클 때 {np.abs(차이_도[:, i]).max():5.2f}도, "
          f"현실이 움직인 폭 {np.rad2deg(np.ptp(현실['잰_각도'][:, i])):6.1f}도")
처음_1도 = 시뮬["시각"][np.argmax(np.abs(차이_도).max(axis=1) > 1.0)]
print(f"두 궤적이 처음 1도 넘게 벌어진 시각: {처음_1도:.2f}초")

그림, 칸들 = plt.subplots(2, 1, figsize=(8, 4.6), sharex=True)
for i, 관절 in enumerate(["어깨", "팔꿈치"]):
    칸들[i].plot(시뮬["시각"], np.rad2deg(시뮬["잰_각도"][:, i]), label="시뮬")
    칸들[i].plot(현실["시각"], np.rad2deg(현실["잰_각도"][:, i]), label="현실 역할", linestyle="--")
    칸들[i].set_ylabel(f"{관절} 각도(도)")
칸들[0].legend(fontsize=8, loc="upper right")
칸들[1].set_xlabel("시간(초)")
그림.tight_layout()
그림.savefig("gap_open_loop.png", dpi=200)
print("저장: gap_open_loop.png")
