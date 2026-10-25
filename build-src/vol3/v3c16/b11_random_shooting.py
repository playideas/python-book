import matplotlib.pyplot as plt
import numpy as np

from 유니사이클 import 굴리기, 목표, 속도_한계, 여유, 장애물, 주기, 회전_한계

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def 여럿_굴리기(상태: np.ndarray, 입력들: np.ndarray) -> np.ndarray:
    """K개의 입력열((K,N,2))을 한꺼번에 굴려 (K,N,3) 상태를 돌려준다."""
    x, y, θ = (np.full(len(입력들), 값) for 값 in 상태)
    기록 = np.empty(입력들.shape[:2] + (3,))
    for k in range(입력들.shape[1]):
        v, ω = 입력들[:, k, 0], 입력들[:, k, 1]
        x, y, θ = x + v * np.cos(θ) * 주기, y + v * np.sin(θ) * 주기, θ + ω * 주기
        기록[:, k] = np.stack([x, y, θ], axis=1)
    return 기록


def 점수(예측들: np.ndarray, 입력들: np.ndarray) -> np.ndarray:
    """비선형 MPC와 같은 비용 + 부딪힌 걸음마다 벌점 1000. 매끄럽지 않아도 괜찮다."""
    거리 = 예측들[:, :, :2] - 목표
    비용 = np.sum(거리**2, axis=(1, 2)) + 5 * np.sum(거리[:, -1]**2, axis=1) + 0.1 * np.sum(입력들[:, :, 1]**2, axis=1)
    부딪힘 = (여유(예측들.reshape(-1, 3)).reshape(len(예측들), -1) < 0).sum(axis=1)
    return 비용 + 1000 * 부딪힘


생성기 = np.random.default_rng(0)
K, N = 300, 20                                      # 후보 300개, 2초 앞까지
상태, 최선 = np.array([0.0, 0.0, 0.0]), np.tile([0.3, 0.0], (N, 1))
경로 = [상태]
그림, 칸 = plt.subplots(figsize=(8, 3.4))
for 걸음 in range(150):
    기준 = np.r_[최선[1:], 최선[-1:]]                 # 지난 최선을 한 칸 당긴 것 주변에 쏜다
    후보들 = 기준 + 생성기.normal(0, [0.2, 0.8], size=(K, N, 2))
    후보들[0] = 기준                                  # 지난 계획도 후보에 넣어 둔다
    후보들[..., 0] = np.clip(후보들[..., 0], *속도_한계)
    후보들[..., 1] = np.clip(후보들[..., 1], *회전_한계)
    예측들 = 여럿_굴리기(상태, 후보들)
    점수들 = 점수(예측들, 후보들)
    최선 = 후보들[np.argmin(점수들)]
    if 걸음 == 8:                                     # 한 순간의 '사격' 모습을 그린다
        for 예측, 값 in zip(예측들, 점수들):
            칸.plot(예측[:, 0], 예측[:, 1], color="tab:red" if 값 >= 1000 else "tab:blue",
                   linewidth=0.5, alpha=0.3)
        칸.plot(*예측들[np.argmin(점수들), :, :2].T, color="black", linewidth=2, label="고른 후보")
        print(f"{걸음}번째 주기: 후보 {K}개 중 부딪히는 것 {(점수들 >= 1000).sum()}개")
    상태 = 굴리기(상태, 최선[:1])[0]
    경로.append(상태)
    if np.linalg.norm(상태[:2] - 목표) < 0.05:
        break
경로 = np.array(경로)
가장_가까이 = 여유(경로).min()
print(f"{len(경로) - 1}주기 뒤 남은 거리 {np.linalg.norm(경로[-1, :2] - 목표):.2f}m, "
      f"최소 여유 {가장_가까이 * 100:.1f}cm")
칸.plot(경로[:, 0], 경로[:, 1], ".-", color="tab:orange", markersize=3, label="실제로 간 길")
for x, y, r in 장애물:
    칸.add_patch(plt.Circle((x, y), r, color="gray"))
칸.plot(*목표, "k*", markersize=12)
칸.plot([], [], color="tab:blue", label="후보(안전)")
칸.plot([], [], color="tab:red", label="후보(부딪힘)")
칸.set_xlabel("x(m)")
칸.set_ylabel("y(m)")
칸.set_aspect("equal")
칸.set_xlim(-0.2, 4.4)
칸.set_ylim(-0.6, 2.1)
칸.legend(fontsize=8, loc="upper left")
그림.tight_layout()
그림.savefig("random_shooting.png", dpi=200)
print("저장: random_shooting.png")
