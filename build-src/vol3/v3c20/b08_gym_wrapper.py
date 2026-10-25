from collections import deque

import gymnasium as gym
import numpy as np


class 무작위화_감싸개(gym.Wrapper):
    """에피소드마다 질량·마찰을 흔들고, 관측에 잡음을, 행동에 지연을 넣는다."""

    def __init__(self, env: gym.Env, 폭: float = 0.3, 잡음: float = 0.01, 최대_지연: int = 2):
        super().__init__(env)
        모델 = env.unwrapped.model
        self.원래_질량 = 모델.body_mass.copy()          # 흔들기 전 값을 기억해 두고 매번 여기서 흔든다
        self.원래_마찰 = 모델.geom_friction.copy()
        self.폭, self.잡음, self.최대_지연 = 폭, 잡음, 최대_지연
        self.생성기 = np.random.default_rng(0)

    def reset(self, **kwargs):
        모델 = self.env.unwrapped.model
        모델.body_mass[:] = self.원래_질량 * self.생성기.uniform(1 - self.폭, 1 + self.폭, len(self.원래_질량))
        모델.geom_friction[:] = self.원래_마찰 * self.생성기.uniform(1 - self.폭, 1 + self.폭)
        self.지연 = int(self.생성기.integers(0, self.최대_지연 + 1))
        self.대기열 = deque([np.zeros(self.action_space.shape)] * self.지연)
        관측, 정보 = self.env.reset(**kwargs)
        return 관측 + self.생성기.normal(0, self.잡음, 관측.shape), 정보

    def step(self, 행동):
        self.대기열.append(np.asarray(행동, dtype=float))
        관측, 보상, 끝남, 잘림, 정보 = self.env.step(self.대기열.popleft())
        return 관측 + self.생성기.normal(0, self.잡음, 관측.shape), 보상, 끝남, 잘림, 정보


env = 무작위화_감싸개(gym.make("InvertedPendulum-v5"))
print("원래 질량(수레, 막대):", np.round(env.원래_질량[1:], 3))
for 에피소드 in range(5):
    관측, _ = env.reset(seed=에피소드)
    걸음 = 0
    while True:
        # 손으로 고른 규칙: 막대가 기운 쪽으로 수레를 민다(관측: 수레 위치, 막대 각도, 두 속도)
        행동 = np.clip([1.0 * 관측[0] + 20 * 관측[1] + 2.0 * 관측[2] + 3.0 * 관측[3]], -3, 3)
        관측, 보상, 끝남, 잘림, _ = env.step(행동)
        걸음 += 1
        if 끝남 or 잘림 or 걸음 >= 1000:
            break
    print(f"에피소드 {에피소드}: 질량 {np.round(env.unwrapped.model.body_mass[1:], 3)}, "
          f"지연 {env.지연}걸음, 버틴 걸음 {걸음}")
