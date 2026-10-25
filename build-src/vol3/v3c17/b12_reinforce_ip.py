import gymnasium as gym
import matplotlib.pyplot as plt
import numpy as np
import torch

from 강화도구 import 가우스정책, 할인_반환값, 한_판

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def REINFORCE(기준선: bool, 씨앗: int, 총_걸음: int = 150_000, 감마: float = 0.99) -> list[tuple[int, float]]:
    """2000걸음어치 판을 모아 한 번 고치기를 되풀이한다. (지금까지 걸음 수, 그때 판 길이 평균)을 기록한다."""
    torch.manual_seed(씨앗)
    환경 = gym.make("InvertedPendulum-v5")
    환경.reset(seed=씨앗)
    정책 = 가우스정책(4, 1)
    최적화기 = torch.optim.Adam(정책.parameters(), lr=3e-3)
    걸음, 곡선 = 0, []
    while 걸음 < 총_걸음:
        상태들, 행동들, 반환값들, 길이들 = [], [], [], []
        while sum(길이들) < 2000:
            상태, 행동, 보상들 = 한_판(환경, 정책)
            상태들.append(상태)
            행동들.append(행동)
            반환값들.append(할인_반환값(보상들, 감마))
            길이들.append(len(보상들))
        G = torch.as_tensor(np.concatenate(반환값들), dtype=torch.float32)
        G = ((G - G.mean()) if 기준선 else G) / (G.std() + 1e-8)       # 크기는 둘 다 맞춰 준다
        분포 = 정책.분포(torch.as_tensor(np.concatenate(상태들)))
        손실 = -(분포.log_prob(torch.as_tensor(np.concatenate(행동들))).sum(-1) * G).mean()
        최적화기.zero_grad()
        손실.backward()
        최적화기.step()
        걸음 += sum(길이들)
        곡선.append((걸음, float(np.mean(길이들))))
    return 곡선


그림, 칸 = plt.subplots(figsize=(7, 3.2))
for 기준선, 색 in [(False, "tab:gray"), (True, "tab:blue")]:
    마지막 = []
    for 씨앗 in range(3):
        곡선 = np.array(REINFORCE(기준선, 씨앗))
        칸.plot(곡선[:, 0], 곡선[:, 1], color=색, alpha=0.8,
               label=("기준선 있음" if 기준선 else "기준선 없음") if 씨앗 == 0 else None)
        마지막.append(곡선[-10:, 1].mean())
    print(f"기준선 {'있음' if 기준선 else '없음'}: 마지막 10번 고칠 때 판 길이 평균 "
          + ", ".join(f"{값:.0f}" for 값 in 마지막) + "걸음 (씨앗 0, 1, 2)")
칸.set_xlabel("모은 걸음 수")
칸.set_ylabel("판 길이 평균(걸음)")
칸.legend()
그림.tight_layout()
그림.savefig("reinforce_curve.png", dpi=200)
print("저장: reinforce_curve.png")
