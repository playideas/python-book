import torch

from 갈림길 import 굴리기, 보폭, 시연
from 여러답정책 import 망

상태, 행동, _ = 시연(100)
print(f"시연 100개(왼쪽 50, 오른쪽 50), 걸음 {len(상태)}개")
X, Y = torch.tensor(상태, dtype=torch.float32), torch.tensor(행동 / 보폭, dtype=torch.float32)
torch.manual_seed(0)
모델 = 망(2, 2)
최적화 = torch.optim.Adam(모델.parameters(), lr=1e-3)
for _ in range(8000):                                    # 18.4절과 같은 MSE 행동 복제
    고른 = torch.randint(0, len(X), (256,))
    손실 = ((모델(X[고른]) - Y[고른]) ** 2).mean()
    최적화.zero_grad()
    손실.backward()
    최적화.step()

with torch.no_grad():
    출발_행동 = 모델(torch.zeros(1, 2))[0]
처음 = 상태[:, 1] < 0.05                                 # 출발 직후 시연 걸음들
print("출발점에서 시연 행동: 왼쪽", (행동[처음 & (행동[:, 0] < 0)] / 보폭).mean(0).round(2),
      "/ 오른쪽", (행동[처음 & (행동[:, 0] > 0)] / 보폭).mean(0).round(2))
print("출발점에서 MSE 정책 :", 출발_행동.numpy().round(2))
_, 성공 = 굴리기(lambda p: 모델(torch.tensor(p, dtype=torch.float32)).detach().numpy(), 100)
print(f"MSE 정책 성공률: {성공.mean():.0%}")
