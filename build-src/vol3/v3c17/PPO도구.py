"""17장: 작은 PPO. 정책망과 가치망, GAE, 클리핑만 담았다."""
import gymnasium as gym
import numpy as np
import torch
from torch import nn

from 강화도구 import 가우스정책


class 행위자비평가(nn.Module):
    """행동을 고르는 정책(행위자)과 상태의 가치를 매기는 가치망(비평가)을 한 몸에."""

    def __init__(self, 상태_수: int, 행동_수: int, 은닉: int = 64):
        super().__init__()
        self.정책 = 가우스정책(상태_수, 행동_수, 은닉)
        self.가치망 = nn.Sequential(nn.Linear(상태_수, 은닉), nn.Tanh(),
                                 nn.Linear(은닉, 은닉), nn.Tanh(),
                                 nn.Linear(은닉, 1))

    def 가치(self, 상태: torch.Tensor) -> torch.Tensor:
        return self.가치망(상태).squeeze(-1)


def 모으기(환경: gym.Env, 모델: 행위자비평가, 걸음_수: int, 상태: np.ndarray, 보상합: float = 0.0):
    """지금 정책으로 걸음_수만큼 해 보고, 학습에 쓸 기록과 끝난 에피소드들의 보상 합을 돌려준다.
    걸음_수에서 끊긴 판은 다음 호출에서 이어지므로, 그 판의 지금 상태와 보상 합도 돌려준다."""
    기록 = {이름: [] for 이름 in ["상태", "행동", "로그확률", "보상", "다음_상태", "끝남", "경계"]}
    끝난_보상합 = []
    for _ in range(걸음_수):
        with torch.no_grad():
            분포 = 모델.정책.분포(torch.as_tensor(상태, dtype=torch.float32))
            행동 = 분포.sample()
        보낼_행동 = np.clip(행동.numpy(), 환경.action_space.low, 환경.action_space.high)
        다음_상태, 보상, 끝남, 잘림, _ = 환경.step(보낼_행동)
        한_줄 = [상태, 행동.numpy(), 분포.log_prob(행동).sum().item(), 보상, 다음_상태, 끝남, 끝남 or 잘림]
        for 이름, 값 in zip(기록, 한_줄):
            기록[이름].append(값)
        보상합 += 보상
        상태 = 다음_상태
        if 끝남 or 잘림:                          # 에피소드가 끝나면 보상 합을 적고 처음부터
            끝난_보상합.append(보상합)
            보상합 = 0.0
            상태, _ = 환경.reset()
    자료 = {이름: torch.as_tensor(np.array(값), dtype=torch.float32) for 이름, 값 in 기록.items()}
    return 자료, 상태, 보상합, 끝난_보상합


def GAE(보상: torch.Tensor, 가치: torch.Tensor, 다음_가치: torch.Tensor, 경계: torch.Tensor,
        감마: float, 람다: float) -> torch.Tensor:
    """한 걸음 놀람 δ = r + γV(s') - V(s)를 뒤에서부터 γλ로 할인해 쌓는다. 에피소드 경계에서 끊는다."""
    이점 = torch.zeros_like(보상)
    누적 = 0.0
    for t in reversed(range(len(보상))):
        델타 = 보상[t] + 감마 * 다음_가치[t] - 가치[t]
        누적 = 델타 + 감마 * 람다 * (1 - 경계[t]) * 누적
        이점[t] = 누적
    return 이점


def 고치기(모델: 행위자비평가, 최적화기: torch.optim.Optimizer, 자료: dict, 이점: torch.Tensor,
         목표_가치: torch.Tensor, 반복: int, 미니배치: int, 클립: float) -> None:
    """모은 자료를 여러 번 나눠 보며, 확률 비율을 1±클립 안에 묶은 목적 함수로 정책과 가치망을 고친다."""
    이점 = (이점 - 이점.mean()) / (이점.std() + 1e-8)
    for _ in range(반복):
        for 번호 in torch.randperm(len(이점)).split(미니배치):
            분포 = 모델.정책.분포(자료["상태"][번호])
            비율 = torch.exp(분포.log_prob(자료["행동"][번호]).sum(-1) - 자료["로그확률"][번호])
            묶은_비율 = torch.clamp(비율, 1 - 클립, 1 + 클립)
            정책_손실 = -torch.min(비율 * 이점[번호], 묶은_비율 * 이점[번호]).mean()
            가치_손실 = ((모델.가치(자료["상태"][번호]) - 목표_가치[번호]) ** 2).mean()
            최적화기.zero_grad()
            (정책_손실 + 0.5 * 가치_손실).backward()
            nn.utils.clip_grad_norm_(모델.parameters(), 0.5)
            최적화기.step()


def 학습(환경: gym.Env, 총_걸음: int, 씨앗: int = 0, 모으는_걸음: int = 2048, 반복: int = 10,
       미니배치: int = 64, 감마: float = 0.99, 람다: float = 0.95, 클립: float = 0.2,
       학습률: float = 3e-4) -> tuple[행위자비평가, list[tuple[int, float]]]:
    """PPO로 정책을 학습하고, (지금까지 걸음 수, 최근 에피소드 10개의 보상 합 평균) 기록을 함께 돌려준다."""
    torch.manual_seed(씨앗)
    모델 = 행위자비평가(환경.observation_space.shape[0], 환경.action_space.shape[0])
    최적화기 = torch.optim.Adam(모델.parameters(), lr=학습률)
    상태, _ = 환경.reset(seed=씨앗)
    보상합, 곡선, 최근 = 0.0, [], []
    for 회차 in range(1, 총_걸음 // 모으는_걸음 + 1):
        자료, 상태, 보상합, 끝난_보상합 = 모으기(환경, 모델, 모으는_걸음, 상태, 보상합)
        with torch.no_grad():
            가치 = 모델.가치(자료["상태"])
            다음_가치 = 모델.가치(자료["다음_상태"]) * (1 - 자료["끝남"])   # 진짜로 끝났으면 앞날은 0
        이점 = GAE(자료["보상"], 가치, 다음_가치, 자료["경계"], 감마, 람다)
        고치기(모델, 최적화기, 자료, 이점, 이점 + 가치, 반복, 미니배치, 클립)
        최근 = (최근 + 끝난_보상합)[-10:]
        곡선.append((회차 * 모으는_걸음, float(np.mean(최근)) if 최근 else float("nan")))
    return 모델, 곡선
