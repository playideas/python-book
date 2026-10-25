import matplotlib.pyplot as plt
import numpy as np

from 식별 import 맞추기, 이름들
from 현실팔 import 시뮬_물성, 실행, 현실_물성

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def 빠른_들뜸(t: float, q: np.ndarray) -> np.ndarray:
    return np.array([3.0 * np.sin(2 * np.pi * 0.7 * t) + 2.0 * np.sin(2 * np.pi * 1.9 * t),
                     1.2 * np.sin(2 * np.pi * 1.1 * t) + 0.8 * np.sin(2 * np.pi * 2.7 * t)])


def 느린_들뜸(t: float, q: np.ndarray) -> np.ndarray:
    return np.array([2.0, 0.8]) * np.sin(2 * np.pi * 0.15 * t)          # 천천히 한 번 오가기


def 검증_토크(t: float, q: np.ndarray) -> np.ndarray:
    """맞출 때 쓰지 않은 새 명령: 0.5초마다 바뀌는 계단 토크."""
    단계 = int(t // 0.5)
    return np.array([[-2.5, 3.5, 0.5, -4.0][단계 % 4], [1.5, -1.0, 2.0, -2.0][단계 % 3]])


모델들 = {"시뮬(처음 적은 값)": 시뮬_물성}
for 이름, 신호 in [("느린 들뜸으로 맞춤", 느린_들뜸), ("빠른 들뜸으로 맞춤", 빠른_들뜸)]:
    p, rms = 맞추기(신호, 실행(신호, 6.0, 현실_물성, 시드=1), 지연=2)
    모델들[이름] = p
    print(f"{이름}: 맞춘 기록에서 남은 차이 {rms:.2f}도 / "
          + ", ".join(f"{n} {getattr(p, n):.3f}" for n in 이름들))

현실 = 실행(검증_토크, 4.0, 현실_물성, 시드=2)
그림, 칸 = plt.subplots(figsize=(8, 3.4))
칸.plot(현실["시각"], np.rad2deg(현실["잰_각도"][:, 1]), color="black", linewidth=2.5, label="현실 역할")
for 이름, p in 모델들.items():
    예측 = 실행(검증_토크, 4.0, p)
    차이 = np.rad2deg(np.sqrt(np.mean((예측["잰_각도"] - 현실["잰_각도"]) ** 2)))
    print(f"새 명령으로 검증 - {이름}: 차이 RMS {차이:5.2f}도")
    칸.plot(예측["시각"], np.rad2deg(예측["잰_각도"][:, 1]), linewidth=1.2, label=이름)
칸.set_xlabel("시간(초)")
칸.set_ylabel("팔꿈치 각도(도)")
칸.legend(fontsize=8, ncol=2)
그림.tight_layout()
그림.savefig("sysid_check.png", dpi=200)
print("저장: sysid_check.png")
