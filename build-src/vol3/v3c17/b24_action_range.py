import numpy as np
import torch

from 강화도구 import 가우스정책

torch.manual_seed(0)
정책 = 가우스정책(3, 1)                                   # 막 만든 정책: 평균은 0 근처, 표준편차 약 0.61
with torch.no_grad():
    행동들 = 정책.분포(torch.zeros(10000, 3)).sample().numpy().ravel()
print(f"뽑은 행동: 평균 {행동들.mean():+.3f}, 표준편차 {행동들.std():.3f}")
for 이름, 한계 in [("-1~1 (이 장의 진자 환경)", 1.0), ("-3~3 (InvertedPendulum)", 3.0),
                 ("-2000~2000 (토크를 mN·m로 받는다면)", 2000.0)]:
    잘린_비율 = np.mean(np.abs(행동들) > 한계)
    print(f"{이름:30s}: 한계에서 잘리는 행동 {잘린_비율:6.1%}, 흩뿌림이 범위의 {행동들.std() / (2 * 한계):.2%}")
