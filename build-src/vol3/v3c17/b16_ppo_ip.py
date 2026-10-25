import gymnasium as gym
import matplotlib.pyplot as plt
import numpy as np
import torch

from PPO도구 import 학습

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

그림, 칸 = plt.subplots(figsize=(7, 3.2))
모델들 = []
for 씨앗 in range(3):
    모델, 곡선 = 학습(gym.make("InvertedPendulum-v5"), 총_걸음=150_000, 씨앗=씨앗)
    곡선 = np.array(곡선)
    칸.plot(곡선[:, 0], 곡선[:, 1], label=f"씨앗 {씨앗}")         # 보상 합 ≈ 버틴 걸음 수
    처음_500 = 곡선[np.argmax(곡선[:, 1] >= 500), 0]
    print(f"씨앗 {씨앗}: 보상 합 평균이 처음 500을 넘은 때 {처음_500:.0f}걸음째, 마지막 기록 {곡선[-1, 1]:.0f}")
    모델들.append(모델)
칸.set_xlabel("모은 걸음 수")
칸.set_ylabel("최근 10판 보상 합 평균")
칸.legend()
그림.tight_layout()
그림.savefig("ppo_ip_curve.png", dpi=200)
print("저장: ppo_ip_curve.png")

# 학습이 끝난 정책은 흩뿌리지 않고 평균 행동만 써서 시험한다
환경 = gym.make("InvertedPendulum-v5")
for 씨앗, 모델 in enumerate(모델들):
    길이들 = []
    for 판 in range(10):
        상태, _ = 환경.reset(seed=100 + 판)
        for 걸음 in range(1, 1001):
            with torch.no_grad():
                행동 = 모델.정책.평균망(torch.as_tensor(상태, dtype=torch.float32)).numpy()
            상태, _, 끝남, 잘림, _ = 환경.step(np.clip(행동, -3, 3))
            if 끝남 or 잘림:
                break
        길이들.append(걸음)
    print(f"씨앗 {씨앗} 정책 시험 10판: {길이들}")
