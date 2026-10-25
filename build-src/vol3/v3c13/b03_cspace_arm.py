import matplotlib.pyplot as plt
import numpy as np

from 팔공간 import 관절_점들, 관절공간_지도, 여유, 장애물들

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

막힘 = 관절공간_지도(간격_도=1)                # 361 × 361 자세를 하나하나 검사
print(f"관절 공간 {막힘.size}칸 중 {막힘.mean() * 100:.1f}%가 장애물")

그림, (왼쪽, 오른쪽) = plt.subplots(1, 2, figsize=(10, 4.8))
for x, y, r in 장애물들:
    왼쪽.add_patch(plt.Circle((x, y), r, color="dimgray"))
자세들 = {"가": (-20, 40), "나": (85, 30), "다": (40, 0), "라": (110, -60)}
for (이름, (a, b)), 색 in zip(자세들.items(), ["tab:blue", "tab:green", "tab:red", "tab:purple"]):
    q = np.deg2rad([a, b])
    print(f"자세 {이름} (어깨 {a:4d}도, 팔꿈치 {b:4d}도): " + ("부딪힘" if 여유(q) < 0 else f"여유 {여유(q):.3f}m"))
    선 = np.vstack([[0, 0], *관절_점들(q)])                 # 바닥, 팔꿈치, 손끝
    왼쪽.plot(*선.T, "o-", color=색, linewidth=3, markersize=4)
    왼쪽.annotate(이름, 선[2], textcoords="offset points", xytext=(5, 5), color=색, fontsize=12)
    오른쪽.plot(a, b, "o", color=색, markersize=7)
    오른쪽.annotate(이름, (a, b), textcoords="offset points", xytext=(6, 4), color=색, fontsize=12)
왼쪽.set(xlim=(-0.8, 0.8), ylim=(-0.8, 0.8), aspect="equal", title="작업 공간: 팔과 장애물",
        xlabel="x (m)", ylabel="y (m)")
오른쪽.imshow(막힘.T, origin="lower", extent=[-180, 180, -180, 180], cmap="gray_r", vmin=0, vmax=1.6)
오른쪽.set(title="관절 공간: 회색은 부딪히는 자세", xlabel="어깨 각도 (도)", ylabel="팔꿈치 각도 (도)")
그림.tight_layout()
그림.savefig("cspace_arm.png", dpi=200)
print("저장: cspace_arm.png")
