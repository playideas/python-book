import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

클립 = 0.2
비율 = np.linspace(0.0, 2.0, 401)                        # 새 정책 확률 / 옛 정책 확률
그림, 칸들 = plt.subplots(1, 2, figsize=(7.5, 2.8), sharey=True)
for 칸, 이점 in zip(칸들, [1.0, -1.0]):
    그대로 = 비율 * 이점
    묶은 = np.clip(비율, 1 - 클립, 1 + 클립) * 이점
    목적 = np.minimum(그대로, 묶은)                         # 둘 중 작은 쪽(비관적인 쪽)을 쓴다
    칸.plot(비율, 그대로, color="lightgray", linestyle="--", label="비율 × 이점")
    칸.plot(비율, 목적, color="tab:blue", linewidth=2, label="PPO 목적")
    칸.axvspan(1 - 클립, 1 + 클립, color="tab:orange", alpha=0.15)
    칸.set_title(f"이점 {'+1 (좋았던 행동)' if 이점 > 0 else '-1 (나빴던 행동)'}")
    칸.set_xlabel("확률 비율")
    print(f"이점 {이점:+.0f}: 비율 0.5→{np.interp(0.5, 비율, 목적):+.2f}, 1.0→{np.interp(1.0, 비율, 목적):+.2f}, "
          f"1.5→{np.interp(1.5, 비율, 목적):+.2f}, 2.0→{np.interp(2.0, 비율, 목적):+.2f}")
칸들[0].set_ylabel("목적 함수 값")
칸들[0].legend(fontsize=8)
그림.tight_layout()
그림.savefig("ppo_clip.png", dpi=200)
print("저장: ppo_clip.png")
