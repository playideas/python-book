import matplotlib.pyplot as plt
import numpy as np

from 무작위화 import kd들, kp들, 가장_좋은_칸, 무작위_물성, 점수표
from 팔제어 import 돌려_보기
from 현실팔 import 시뮬_물성, 현실_물성

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

생성기 = np.random.default_rng(0)
흔든_팔들 = [무작위_물성(생성기) for _ in range(20)]          # 에피소드마다 다른 팔 20대
print("흔든 팔 셋만 보기:")
for 팔 in 흔든_팔들[:3]:
    print(f"  끝 질량 {팔.끝_질량:.2f}kg, 감쇠 {팔.감쇠:.2f}, 마찰 {팔.마찰:.2f}, 토크 배율 {팔.토크_배율:.2f}, "
          f"지연 {팔.지연}틱, 잡음 {np.rad2deg(팔.잡음):.2f}도, 유격 {np.rad2deg(팔.유격):.2f}도")

표들 = {"시뮬 한 대에서": 점수표(시뮬_물성, [시뮬_물성]), "흔든 팔 20대 평균": 점수표(시뮬_물성, 흔든_팔들)}
그림, 칸들 = plt.subplots(1, 2, figsize=(9, 3.6))
for 칸, (이름, 표) in zip(칸들, 표들.items()):
    kp, kd = 가장_좋은_칸(표)
    현실 = [돌려_보기(kp, kd, 시뮬_물성, 현실_물성, 시드) for 시드 in range(10)]
    print(f"{이름} 고른 칸: kp={kp}, kd={kd} (고를 때 점수 {표.min():.2f}도) → "
          f"현실 10번: 평균 오차 {np.mean([r[0] for r in 현실]):.2f}도, 못 감 {sum(r[1] for r in 현실)}/40")
    칸.imshow(표, cmap="viridis_r", vmin=3, vmax=15, origin="lower")
    for i in range(len(kp들)):
        for j in range(len(kd들)):
            칸.text(j, i, f"{표[i, j]:.1f}", ha="center", va="center", fontsize=7,
                   color="white" if 표[i, j] > 9 else "black")
    칸.add_patch(plt.Rectangle((kd들.index(kd) - 0.5, kp들.index(kp) - 0.5), 1, 1, fill=False, edgecolor="red", linewidth=2))
    칸.set_xticks(range(len(kd들)), kd들)
    칸.set_yticks(range(len(kp들)), kp들)
    칸.set_xlabel("kd")
    칸.set_ylabel("kp")
    칸.set_title(f"{이름} (평균 오차, 도)", fontsize=10)
그림.tight_layout()
그림.savefig("dr_grid.png", dpi=200)
print("저장: dr_grid.png")
