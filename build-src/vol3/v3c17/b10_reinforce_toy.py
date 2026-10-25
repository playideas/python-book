import torch

torch.manual_seed(0)
평균 = torch.zeros(1, requires_grad=True)                 # 정책: 평균이 '평균', 표준편차 0.5인 정규 분포
최적화기 = torch.optim.SGD([평균], lr=0.05)


def 보상(행동: torch.Tensor) -> torch.Tensor:
    return -(행동 - 1.5) ** 2                            # 1.5에 가깝게 던질수록 좋다(에이전트는 모른다)


for 회 in range(1, 201):
    분포 = torch.distributions.Normal(평균, 0.5)
    행동들 = 분포.sample((16,))                           # 16번 던져 보고
    보상들 = 보상(행동들)
    손실 = -(분포.log_prob(행동들) * 보상들).mean()         # 보상이 큰 행동의 로그 확률을 올린다
    최적화기.zero_grad()
    손실.backward()
    최적화기.step()
    if 회 in (1, 10, 50, 100, 200):
        print(f"{회:3d}회: 평균 {평균.item():.3f}, 16번 던진 보상 평균 {보상들.mean().item():.3f}")
