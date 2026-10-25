"""18장: 답이 여럿인 행동을 배우는 두 정책. 혼합 가우시안(MDN)과 작은 확산 정책."""
import torch
from torch import nn

torch.set_num_threads(4)                 # 스레드 수를 고정해야 결과가 실행마다 똑같다


def 망(입력: int, 출력: int, 너비: int = 128) -> nn.Sequential:
    return nn.Sequential(nn.Linear(입력, 너비), nn.ReLU(), nn.Linear(너비, 너비), nn.ReLU(),
                         nn.Linear(너비, 출력))


class 혼합가우시안(nn.Module):
    """상태 → 종 모양(가우시안) K개의 비중·가운데·퍼짐. 행동은 그중 하나를 골라 뽑는다."""

    def __init__(self, 상태_크기: int, 행동_크기: int, K: int = 5) -> None:
        super().__init__()
        self.K, self.D = K, 행동_크기
        self.망 = 망(상태_크기, K * (1 + 2 * 행동_크기))

    def 나누기(self, 상태: torch.Tensor):
        출력 = self.망(상태).view(-1, self.K, 1 + 2 * self.D)
        return 출력[..., 0], 출력[..., 1:1 + self.D], 출력[..., 1 + self.D:].clamp(-7, 2)

    def 손실(self, 상태: torch.Tensor, 행동: torch.Tensor) -> torch.Tensor:
        """음의 로그 가능도: 시연 행동이 섞인 종 모양 아래에서 얼마나 그럴듯한가."""
        비중, 가운데, 로그퍼짐 = self.나누기(상태)
        로그p = (-0.5 * ((행동[:, None] - 가운데) / 로그퍼짐.exp()) ** 2 - 로그퍼짐).sum(-1)
        return -torch.logsumexp(로그p + torch.log_softmax(비중, -1), -1).mean()

    @torch.no_grad()
    def 뽑기(self, 상태: torch.Tensor, 생성기: torch.Generator) -> torch.Tensor:
        비중, 가운데, 로그퍼짐 = self.나누기(상태)
        k = torch.multinomial(torch.softmax(비중, -1), 1, generator=생성기)[:, 0]   # 종 하나 고르기
        i = torch.arange(len(상태))
        return 가운데[i, k] + 로그퍼짐[i, k].exp() * torch.randn(len(상태), self.D, generator=생성기)


class 확산정책(nn.Module):
    """2권 15장의 DDPM을 행동에: 잡음 낀 행동과 상태, 단계를 받아 섞인 잡음을 맞힌다."""

    def __init__(self, 상태_크기: int, 행동_크기: int, T: int = 50) -> None:
        super().__init__()
        self.T, self.D = T, 행동_크기
        self.베타 = torch.linspace(1e-4, 0.2, T)          # 행동은 작아서 50단계면 충분하다
        self.알파 = 1 - self.베타
        self.알파_누적 = torch.cumprod(self.알파, 0)
        self.망 = 망(상태_크기 + 행동_크기 + 1, 행동_크기, 너비=256)

    def 잡음_맞히기(self, 상태, 잡음_행동, t) -> torch.Tensor:
        return self.망(torch.cat([상태, 잡음_행동, t[:, None] / self.T], 1))

    def 손실(self, 상태: torch.Tensor, 행동: torch.Tensor) -> torch.Tensor:
        t = torch.randint(0, self.T, (len(상태),))
        잡음 = torch.randn_like(행동)
        a = self.알파_누적[t][:, None]
        return ((self.잡음_맞히기(상태, a.sqrt() * 행동 + (1 - a).sqrt() * 잡음, t) - 잡음) ** 2).mean()

    @torch.no_grad()
    def 뽑기(self, 상태: torch.Tensor, 생성기: torch.Generator) -> torch.Tensor:
        x = torch.randn(len(상태), self.D, generator=생성기)        # 순수한 잡음에서 출발
        for i in reversed(range(self.T)):
            예측 = self.잡음_맞히기(상태, x, torch.full((len(상태),), i))
            x = (x - self.베타[i] / (1 - self.알파_누적[i]).sqrt() * 예측) / self.알파[i].sqrt()
            if i > 0:
                x = x + self.베타[i].sqrt() * torch.randn(x.shape, generator=생성기)
        return x


def 학습(종류: type, 상태, 행동, 걸음: int = 8000, 씨앗: int = 0) -> nn.Module:
    """종류(혼합가우시안 또는 확산정책)의 모델을 만들어 시연을 배운다. 씨앗을 먼저 정해야 결과가 같다."""
    torch.manual_seed(씨앗)
    모델 = 종류(상태.shape[1], 행동.shape[1])
    X, Y = torch.tensor(상태, dtype=torch.float32), torch.tensor(행동, dtype=torch.float32)
    최적화 = torch.optim.Adam(모델.parameters(), lr=1e-3)
    for _ in range(걸음):
        고른 = torch.randint(0, len(X), (256,))
        손실 = 모델.손실(X[고른], Y[고른])
        최적화.zero_grad()
        손실.backward()
        최적화.step()
    return 모델
