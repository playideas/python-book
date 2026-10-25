import time

import gymnasium as gym
import torch

from PPO도구 import 학습
from 진자흔들기환경 import 진자흔들기환경

환경 = gym.wrappers.TransformReward(진자흔들기환경(), lambda r: 0.1 * r)
시작 = time.perf_counter()
모델, 곡선 = 학습(환경, 총_걸음=300_000, 씨앗=0)
걸린_시간 = time.perf_counter() - 시작
print(f"학습: {곡선[-1][0]}걸음(시뮬레이션 속 {곡선[-1][0] * 0.01 / 60:.0f}분어치), 이 맥에서 {걸린_시간:.0f}초")

torch.save(모델.state_dict(), "흔들기_정책.pt")            # 2권 6장처럼 숫자(state_dict)만 저장한다
print("저장: 흔들기_정책.pt,", sum(p.numel() for p in 모델.parameters()), "개 숫자")
