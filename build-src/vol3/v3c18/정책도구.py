"""18장: 관측 → 행동을 배우는 MLP 정책(2권 6장의 학습 루프)."""
import numpy as np
import torch
from torch import nn

torch.set_num_threads(4)                 # 스레드 수를 고정해야 결과가 실행마다 똑같다


class MLP정책(nn.Module):
    """관측 하나를 받아 앞으로 '묶음' 걸음 동안의 행동을 한꺼번에 낸다. 묶음=1이면 보통의 BC."""

    def __init__(self, 관측: np.ndarray, 행동: np.ndarray, 너비: int = 256) -> None:
        super().__init__()
        _, self.묶음, self.행동_크기 = 행동.shape               # 행동: (개수, 묶음, 행동 크기)
        self.관측_크기 = 관측.shape[1]                          # 관측 벡터의 앞에서부터 이만큼만 본다
        # 표준편차가 0에 가까운 칸(늘 0인 손목1 등)으로 나누면 작은 차이가 수천 배로 커진다
        self.관측_평균, self.관측_표준 = 관측.mean(0), np.maximum(관측.std(0), 0.01)
        self.행동_평균, self.행동_표준 = 행동.mean((0, 1)), np.maximum(행동.std((0, 1)), 0.01)
        self.망 = nn.Sequential(nn.Linear(관측.shape[1], 너비), nn.ReLU(),
                               nn.Linear(너비, 너비), nn.ReLU(),
                               nn.Linear(너비, self.묶음 * self.행동_크기))

    def 정규화(self, 관측: np.ndarray, 행동: np.ndarray | None = None):
        x = torch.tensor((관측 - self.관측_평균) / self.관측_표준, dtype=torch.float32)
        if 행동 is None:
            return x
        y = (행동 - self.행동_평균) / self.행동_표준
        return x, torch.tensor(y.reshape(len(y), -1), dtype=torch.float32)

    @torch.no_grad()
    def 덩어리(self, 관측: np.ndarray) -> np.ndarray:
        """관측 하나 → (묶음, 행동 크기)짜리 행동 덩어리."""
        y = self.망(self.정규화(관측[None, :self.관측_크기]))[0].view(self.묶음, self.행동_크기).numpy()
        return y * self.행동_표준 + self.행동_평균

    def __call__(self, 관측: np.ndarray) -> np.ndarray:
        """정책으로 쓸 때: 관측 하나 → 지금 할 행동 하나(numpy)."""
        return self.덩어리(관측)[0]


def 덩어리_만들기(행동: np.ndarray, 에피소드: np.ndarray, 묶음: int) -> np.ndarray:
    """걸음마다 '지금부터 묶음 걸음 동안의 행동'을 모은다. 에피소드 끝을 넘으면 마지막 행동으로 채운다."""
    덩어리 = np.empty((len(행동), 묶음, 행동.shape[1]))
    for i in range(len(행동)):
        끝 = np.searchsorted(에피소드, 에피소드[i], side="right") - 1    # 같은 에피소드의 마지막 걸음
        덩어리[i] = 행동[np.minimum(np.arange(i, i + 묶음), 끝)]
    return 덩어리


def 학습(관측: np.ndarray, 행동: np.ndarray, 걸음: int = 20000, 씨앗: int = 0) -> MLP정책:
    """행동을 MSE로 따라 배운다. 행동은 (개수, 행동 크기) 또는 (개수, 묶음, 행동 크기)."""
    torch.manual_seed(씨앗)
    행동 = 행동 if 행동.ndim == 3 else 행동[:, None]
    정책 = MLP정책(관측, 행동)
    X, Y = 정책.정규화(관측, 행동)
    최적화 = torch.optim.Adam(정책.parameters(), lr=1e-3)
    생성기 = torch.Generator().manual_seed(씨앗)
    for _ in range(걸음):
        고른 = torch.randint(0, len(X), (256,), generator=생성기)
        손실 = ((정책.망(X[고른]) - Y[고른]) ** 2).mean()
        최적화.zero_grad()
        손실.backward()
        최적화.step()
    return 정책


@torch.no_grad()
def 검증_손실(정책: MLP정책, 관측: np.ndarray, 행동: np.ndarray) -> float:
    X, Y = 정책.정규화(관측, 행동 if 행동.ndim == 3 else 행동[:, None])
    return float(((정책.망(X) - Y) ** 2).mean())
