import gymnasium as gym
import numpy as np

from PPO도구 import 학습
from 진자흔들기환경 import 진자흔들기환경
from 흔들기시험 import 시험, 평균_행동


def 각도_그대로(상태: np.ndarray) -> np.ndarray:
    """[cos θ, sin θ, 각속도]를 [θ(-π~π), 각속도]로 바꾼다. 거꾸로 선 자세가 +π와 -π 두 곳에 있다."""
    return np.array([np.arctan2(상태[1], 상태[0]), 상태[2]], dtype=np.float32)


def 만들기(관측_방식: str) -> gym.Env:
    환경 = gym.wrappers.TransformReward(진자흔들기환경(), lambda r: 0.1 * r)
    if 관측_방식 == "각도 그대로":
        공간 = gym.spaces.Box(-np.inf, np.inf, shape=(2,), dtype=np.float32)
        환경 = gym.wrappers.TransformObservation(환경, 각도_그대로, 공간)
    if 관측_방식 == "cos·sin + 정규화":
        환경 = gym.wrappers.NormalizeObservation(환경)           # 지금까지 본 관측의 평균·표준편차로 맞춘다
    return 환경


for 관측_방식 in ["각도 그대로", "cos·sin", "cos·sin + 정규화"]:
    환경 = 만들기(관측_방식)
    모델, _ = 학습(환경, 총_걸음=200_000, 씨앗=0)
    if 관측_방식 == "cos·sin + 정규화":
        환경.update_running_mean = False                         # 시험 때는 평균·표준편차를 더 고치지 않는다
    결과 = 시험(환경, 평균_행동(모델))
    print(f"{관측_방식:12s}: 시험 20판 성공률 {결과['성공률']:4.0%}")
