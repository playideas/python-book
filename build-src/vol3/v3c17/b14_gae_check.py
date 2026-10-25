import torch

from PPO도구 import GAE
from 강화도구 import 할인_반환값

보상 = torch.tensor([0.0, 0.0, 0.0, 1.0])                 # 마지막 걸음에서만 보상
가치 = torch.tensor([0.5, 0.6, 0.8, 0.9])                 # 가치망의 지금 어림(예제용 숫자)
다음_가치 = torch.tensor([0.6, 0.8, 0.9, 0.0])            # 마지막 다음은 끝났으니 0
경계 = torch.tensor([0.0, 0.0, 0.0, 1.0])
감마 = 0.9

print("λ=0  :", GAE(보상, 가치, 다음_가치, 경계, 감마, 0.0).numpy().round(3))
print("한 걸음 놀람 δ:", (보상 + 감마 * 다음_가치 - 가치).numpy().round(3))
print("λ=1  :", GAE(보상, 가치, 다음_가치, 경계, 감마, 1.0).numpy().round(3))
print("G - V:", (torch.tensor(할인_반환값(보상.tolist(), 감마)) - 가치).numpy().round(3))
print("λ=0.95:", GAE(보상, 가치, 다음_가치, 경계, 감마, 0.95).numpy().round(3))
