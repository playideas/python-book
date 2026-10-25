import gymnasium as gym
import matplotlib.pyplot as plt
import numpy as np

from PPO도구 import 학습
from 진자흔들기환경 import 진자흔들기환경
from 흔들기시험 import 시험, 평균_행동

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

그림, 칸 = plt.subplots(figsize=(7, 3.2))
성공률들 = []
for 씨앗 in range(5):                                     # 설정은 모두 같고 씨앗만 다르다
    환경 = gym.wrappers.TransformReward(진자흔들기환경(), lambda r: 0.1 * r)
    모델, 곡선 = 학습(환경, 총_걸음=200_000, 씨앗=씨앗)
    곡선 = np.array(곡선)
    칸.plot(곡선[:, 0], 곡선[:, 1] / 0.1, label=f"씨앗 {씨앗}")
    결과 = 시험(환경, 평균_행동(모델))
    성공률들.append(결과["성공률"])
    print(f"씨앗 {씨앗}: 마지막 보상 합 평균 {곡선[-1, 1] / 0.1:6.0f}, 시험 20판 성공률 {결과['성공률']:4.0%}")
print(f"다섯 씨앗 성공률 평균 {np.mean(성공률들):.0%}, 가장 나쁨 {min(성공률들):.0%}, 가장 좋음 {max(성공률들):.0%}")
칸.set_xlabel("모은 걸음 수")
칸.set_ylabel("최근 10판 보상 합 평균")
칸.legend(fontsize=8)
그림.tight_layout()
그림.savefig("seeds.png", dpi=200)
print("저장: seeds.png")
