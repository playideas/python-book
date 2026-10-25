import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

이름들 = ["base_link"] + [f"link{i}" for i in range(1, 7)] + ["tip"]
행렬들 = np.load("arm6_tf.npy")                     # 컨테이너에서 tf2로 받아 둔 T_바닥_좌표계

그림 = plt.figure(figsize=(9, 4.6))
칸들 = 그림.add_gridspec(1, 2, width_ratios=[1, 1.6])
# 왼쪽: tf 나무. 부모에서 자식으로 화살표, 관절 이름과 종류를 옆에 적는다
나무 = 그림.add_subplot(칸들[0])
for i, 이름 in enumerate(이름들):
    나무.text(0, -i, 이름, ha="center", va="center", fontsize=10,
            bbox=dict(boxstyle="round", fc="lightyellow" if 이름 != "tip" else "lavender"))
    if i > 0:
        나무.annotate("", xy=(0, -i + 0.3), xytext=(0, -i + 0.7), arrowprops=dict(arrowstyle="->"))
        설명 = "tip_joint (fixed → /tf_static)" if 이름 == "tip" else f"joint{i} (revolute → /tf)"
        나무.text(0.12, -i + 0.5, 설명, va="center", fontsize=8, color="dimgray")
나무.set_xlim(-0.4, 1.3)
나무.set_ylim(-len(이름들) + 0.4, 0.6)
나무.axis("off")
나무.set_title("tf 나무: 좌표계마다 부모가 하나", fontsize=10)

# 오른쪽: 각 좌표계의 원점과 축(x 빨강, y 초록, z 파랑)
칸 = 그림.add_subplot(칸들[1], projection="3d")
원점들 = 행렬들[:, :3, 3]
칸.plot(*원점들.T, "-", color="silver", linewidth=4)
for 이름, T in zip(이름들, 행렬들):
    for 열, 색 in zip(range(3), ["tab:red", "tab:green", "tab:blue"]):
        칸.plot(*zip(T[:3, 3], T[:3, 3] + 0.06 * T[:3, 열]), color=색, linewidth=1.5)
for 이름 in ["base_link", "link3", "tip"]:
    칸.text(*(행렬들[이름들.index(이름)][:3, 3] + [0.02, 0.02, 0.03]), 이름, fontsize=8)
칸.set_xlim(-0.1, 0.5)
칸.set_ylim(-0.1, 0.5)
칸.set_zlim(0, 0.6)
칸.set_box_aspect((1, 1, 1))
칸.set_xticks([0, 0.2, 0.4])
칸.set_yticks([0, 0.2, 0.4])
칸.set_xlabel("x (m)")
칸.set_ylabel("y (m)")
칸.set_zlabel("z (m)")
칸.view_init(elev=20, azim=-60)
칸.set_title("tf2로 받은 좌표계들 (30, 45, 60, 0, 45, 0)도", fontsize=10)
그림.tight_layout()
그림.savefig("tf_tree.png", dpi=200)
print("저장: tf_tree.png")
