"""17장: 정책 신경망과 할인된 보상 합. REINFORCE와 PPO가 함께 쓴다."""
import numpy as np
import torch
from torch import nn

torch.set_num_threads(1)          # 작은 신경망: 스레드 하나로 돌려 실행마다 결과가 똑같게


class 가우스정책(nn.Module):
    """상태를 받아 행동의 평균을 내고, 학습되는 표준편차만큼 흩뿌려 행동을 뽑는 정책."""

    def __init__(self, 상태_수: int, 행동_수: int, 은닉: int = 64):
        super().__init__()
        self.평균망 = nn.Sequential(nn.Linear(상태_수, 은닉), nn.Tanh(),
                                 nn.Linear(은닉, 은닉), nn.Tanh(),
                                 nn.Linear(은닉, 행동_수))
        self.로그_표준편차 = nn.Parameter(torch.full((행동_수,), -0.5))   # 처음 표준편차 약 0.6

    def 분포(self, 상태: torch.Tensor) -> torch.distributions.Normal:
        return torch.distributions.Normal(self.평균망(상태), self.로그_표준편차.exp())


def 할인_반환값(보상들: list[float], 감마: float) -> np.ndarray:
    """각 시점부터 끝까지의 할인된 보상 합 G_t = r_t + γ·G_(t+1)을 뒤에서부터 계산한다."""
    반환값 = np.zeros(len(보상들))
    누적 = 0.0
    for t in reversed(range(len(보상들))):
        누적 = 보상들[t] + 감마 * 누적
        반환값[t] = 누적
    return 반환값


def 한_판(환경, 정책: 가우스정책, 씨앗: int | None = None) -> tuple[np.ndarray, np.ndarray, list[float]]:
    """정책으로 에피소드 하나를 끝까지 해 보고 상태들, 행동들, 보상들을 돌려준다."""
    상태, _ = 환경.reset(seed=씨앗)
    상태들, 행동들, 보상들 = [], [], []
    while True:
        with torch.no_grad():
            행동 = 정책.분포(torch.as_tensor(상태, dtype=torch.float32)).sample().numpy()
        다음_상태, 보상, 끝남, 잘림, _ = 환경.step(np.clip(행동, 환경.action_space.low, 환경.action_space.high))
        상태들.append(상태)
        행동들.append(행동)
        보상들.append(보상)
        상태 = 다음_상태
        if 끝남 or 잘림:
            return np.array(상태들, dtype=np.float32), np.array(행동들, dtype=np.float32), 보상들
