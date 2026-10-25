import numpy as np
from gymnasium.utils.env_checker import check_env

from 진자흔들기환경 import 진자흔들기환경

환경 = 진자흔들기환경()
check_env(환경)                                          # Gymnasium 약속을 지키는지 검사(어기면 오류)
print("검사 통과 / 관측 공간:", 환경.observation_space, "/ 행동 공간:", 환경.action_space)

상태, _ = 환경.reset(seed=0)
print("처음 관측 [cos θ, sin θ, 각속도]:", 상태.round(3))
for 이름, 행동_고르기 in [("가만히", lambda: np.zeros(1)), ("무작위", 환경.action_space.sample)]:
    환경.action_space.seed(0)
    상태, _ = 환경.reset(seed=0)
    보상합, 걸음, 잘림 = 0.0, 0, False
    while not 잘림:
        상태, 보상, 끝남, 잘림, 정보 = 환경.step(행동_고르기())
        보상합 += 보상
        걸음 += 1
    print(f"{이름}: {걸음}걸음 뒤 잘림, 보상 합 {보상합:.0f}, 마지막 오차 {정보['오차_도']:.0f}도")
