import gymnasium as gym
import matplotlib.pyplot as plt
import numpy as np

from PPO도구 import 학습
from 진자흔들기환경 import 진자흔들기환경
from 흔들기시험 import 평균_행동

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def 높이_보상(각도: float, 각속도: float, 토크: float) -> float:
    return float(-np.cos(각도))                            # 추가 높을수록 상: 매달리면 -1, 거꾸로 서면 +1


def 높이_빠르기_보상(각도: float, 각속도: float, 토크: float) -> float:
    return float(-np.cos(각도) + 0.1 * abs(각속도))          # "흔들기를 부추기자"며 빠르기에 덤을 줬다


그림, 칸 = plt.subplots(figsize=(7, 3.2))
for 이름, 보상_함수 in [("높이만", 높이_보상), ("높이 + 빠르기 덤", 높이_빠르기_보상)]:
    환경 = gym.wrappers.TransformReward(진자흔들기환경(보상_함수=보상_함수), lambda r: 0.1 * r)
    모델, _ = 학습(환경, 총_걸음=200_000, 씨앗=0)
    정책 = 평균_행동(모델)
    상태, _ = 환경.reset(seed=1000)
    각도들, 보상들, 잘림 = [], [], False
    while not 잘림:
        상태, 보상, _, 잘림, 정보 = 환경.step(정책(상태))
        각도들.append(환경.unwrapped.데이터.qpos[0])
        보상들.append(보상 / 0.1)
    각도들 = np.array(각도들)
    칸.plot(np.arange(1, 601) * 0.01, np.rad2deg(각도들), label=이름)
    print(f"{이름:10s}: 6초 동안 {abs(각도들[-1] - 각도들[0]) / (2 * np.pi):4.1f}바퀴, "
          f"마지막 오차 {정보['오차_도']:5.1f}도, 한 걸음 보상 평균 {np.mean(보상들):.2f}")
칸.set_xlabel("시간(초)")
칸.set_ylabel("각도(도, 감지 않음)")
칸.legend()
그림.tight_layout()
그림.savefig("reward_hack.png", dpi=200)
print("저장: reward_hack.png")
