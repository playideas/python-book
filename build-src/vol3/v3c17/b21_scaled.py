import gymnasium as gym
import matplotlib.pyplot as plt
import numpy as np

from PPO도구 import 학습
from 진자흔들기환경 import 진자흔들기환경
from 흔들기시험 import 시험, 평균_행동

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

그림, 칸 = plt.subplots(figsize=(7, 3.2))
for 배율 in [1.0, 0.1]:
    환경 = gym.wrappers.TransformReward(진자흔들기환경(), lambda r: 배율 * r)
    모델, 곡선 = 학습(환경, 총_걸음=200_000, 씨앗=0)
    곡선 = np.array(곡선)
    칸.plot(곡선[:, 0], 곡선[:, 1] / 배율, label=f"보상 × {배율}")   # 원래 크기로 되돌려 그린다
    결과 = 시험(환경, 평균_행동(모델))
    print(f"보상 × {배율}: 시험 20판 성공률 {결과['성공률']:.0%}", end="")
    if 결과["올라선_시각"]:
        print(f", 올라선 시각 평균 {np.mean(결과['올라선_시각']):.2f}초", end="")
    print()
칸.set_xlabel("모은 걸음 수")
칸.set_ylabel("최근 10판 보상 합 평균")
칸.legend()
그림.tight_layout()
그림.savefig("reward_scale.png", dpi=200)
print("저장: reward_scale.png")
