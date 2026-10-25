import gymnasium as gym
import numpy as np

from 강화도구 import 할인_반환값


def 가치_어림(정책, 판_수: int = 20, 감마: float = 0.99) -> tuple[float, float]:
    """처음 상태에서 정책대로 여러 판 해 보고 할인된 보상 합의 평균과 표준편차를 낸다."""
    환경 = gym.make("InvertedPendulum-v5")
    환경.action_space.seed(0)
    반환값들 = []
    for 판 in range(판_수):
        상태, _ = 환경.reset(seed=판)
        보상들 = []
        while True:
            상태, 보상, 끝남, 잘림, _ = 환경.step(정책(환경, 상태))
            보상들.append(보상)
            if 끝남 or 잘림:
                break
        반환값들.append(할인_반환값(보상들, 감마)[0])
    return float(np.mean(반환값들)), float(np.std(반환값들))


아무렇게나 = lambda 환경, 상태: 환경.action_space.sample()
손으로_짠 = lambda 환경, 상태: np.clip([np.dot([1, 10, 1, 1], 상태)], -3, 3)
for 이름, 정책 in [("무작위 정책", 아무렇게나), ("손으로 짠 정책", 손으로_짠)]:
    평균, 표준편차 = 가치_어림(정책)
    print(f"{이름}: 처음 상태의 가치 ≈ {평균:6.2f} (판마다 ±{표준편차:.2f})")
