"""17장: 흔들어 올리기 정책을 여러 판 시험해 성공률과 올라선 시각을 잰다."""
from collections.abc import Callable

import gymnasium as gym
import numpy as np
import torch

from PPO도구 import 행위자비평가


def 평균_행동(모델: 행위자비평가) -> Callable[[np.ndarray], np.ndarray]:
    """학습한 정책을 시험할 때는 흩뿌리지 않고 평균 행동만 쓴다."""
    def 정책(상태: np.ndarray) -> np.ndarray:
        with torch.no_grad():
            return 모델.정책.평균망(torch.as_tensor(상태, dtype=torch.float32)).numpy()
    return 정책


def 시험(환경: gym.Env, 정책: Callable[[np.ndarray], np.ndarray], 판_수: int = 20) -> dict:
    """씨앗 1000, 1001, ...으로 판을 돌려 '마지막 1초 동안 10도 안'을 성공으로 센다."""
    올라선_시각, 성공 = [], 0
    for 판 in range(판_수):
        상태, _ = 환경.reset(seed=1000 + 판)
        오차들 = []
        잘림 = False
        while not 잘림:
            상태, _, _, 잘림, 정보 = 환경.step(정책(상태))
            오차들.append(정보["오차_도"])
        오차들 = np.array(오차들)
        if 오차들[-100:].max() < 10:
            성공 += 1
            올라선_시각.append((np.argmax(오차들 < 10) + 1) * 0.01)
    return {"성공률": 성공 / 판_수, "올라선_시각": 올라선_시각}
