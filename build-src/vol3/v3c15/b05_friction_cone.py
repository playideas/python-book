import matplotlib.pyplot as plt
import mujoco
import numpy as np

from 집게시험장면 import 들기, 만들기, 흘려보내기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

마찰 = 1.0
그림, 칸 = plt.subplots(figsize=(5.2, 3.6))
칸.fill_between([0, 3.5], [0, 3.5 * 마찰], [0, -3.5 * 마찰], color="tab:green", alpha=0.12, label="마찰 원뿔 안")
for 쥐는_힘, 색 in [(1.1, "tab:red"), (1.5, "tab:orange"), (3.0, "tab:blue")]:
    모델, 데이터 = 만들기(쥐는_힘=쥐는_힘, 상자_질량=0.2)
    데이터.ctrl[모델.actuator("grip").id] = 0.0
    흘려보내기(모델, 데이터, 0.5)
    들기(모델, 데이터, 0.03)                                     # 3cm 들고 가만히
    for 패드 in ["pad_l", "pad_r"]:
        합 = np.zeros(3)
        힘 = np.zeros(6)
        for i, c in enumerate(데이터.contact[:데이터.ncon]):
            if 모델.geom(패드).id in (c.geom1, c.geom2):
                mujoco.mj_contactForce(모델, 데이터, i, 힘)
                합 += c.frame.reshape(3, 3).T @ 힘[:3]               # 접촉 좌표계 → 세계 좌표계
        수직 = abs(합[1])                                             # 패드는 y축을 따라 상자를 누른다
        접선 = np.linalg.norm(합[[0, 2]])
        print(f"쥐는 힘 {쥐는_힘}N, {패드}: 수직 {수직:.3f}N, 접선 {접선:.3f}N, 접선/수직 {접선 / 수직:.2f} (μ = {마찰})")
        칸.plot(수직, 접선, "o", color=색, label=f"쥐는 힘 {쥐는_힘}N" if 패드 == "pad_l" else None)
        칸.annotate("", (수직, 접선), (0, 0), arrowprops={"arrowstyle": "->", "color": 색})
칸.set_xlabel("수직력 N (패드가 누르는 힘)")
칸.set_ylabel("접선력 (마찰이 버티는 힘)")
칸.set_xlim(0, 3.5)
칸.set_ylim(-1.5, 2.5)
칸.legend(fontsize=8, loc="upper left")
그림.tight_layout()
그림.savefig("friction_cone.png", dpi=200)
print("저장: friction_cone.png")
