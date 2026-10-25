import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

기록 = np.loadtxt("trace.csv", delimiter=",")          # 컨테이너가 tf로 기록한 값
관절각 = np.rad2deg(기록[:, :3])
원점들 = 기록[:, 3:].reshape(len(기록), 5, 3)            # 걸음마다 좌표계 5개의 원점
손끝 = 원점들[:, -1]

그림 = plt.figure(figsize=(10, 3.8))
칸 = 그림.add_subplot(1, 3, 1, projection="3d")
for k in range(0, len(기록), 12):                        # 몇 걸음만 팔 모양을 그린다
    칸.plot(*원점들[k].T, "o-", color="dimgray", alpha=0.5, markersize=2)
칸.plot(*손끝.T, color="tab:red", linewidth=2)
칸.set_xlim(0, 0.3)
칸.set_ylim(-0.15, 0.15)
칸.set_zlim(0, 0.3)
칸.set_box_aspect((1, 1, 1))
칸.set_xticks([0, 0.1, 0.2, 0.3])
칸.set_yticks([-0.1, 0, 0.1])
칸.view_init(elev=25, azim=-130)
칸.set_title("팔과 손끝 궤적", fontsize=10)

위 = 그림.add_subplot(1, 3, 2)
위.plot(손끝[:, 0], 손끝[:, 1], color="tab:red")
위.plot(0, 0, "ks")
위.set_aspect("equal")
위.set_xlabel("x (m)")
위.set_ylabel("y (m)")
위.set_title("위에서 본 손끝(높이 0.05m)", fontsize=10)

관절 = 그림.add_subplot(1, 3, 3)
for i, 이름 in enumerate(["pan", "lift", "elbow"]):
    관절.plot(관절각[:, i], label=이름)
관절.set_xlabel("걸음")
관절.set_ylabel("관절 각도(도)")
관절.legend(fontsize=8)
관절.set_title("발행한 관절 각도", fontsize=10)
그림.tight_layout()
그림.savefig("trace.png", dpi=200)
print("저장: trace.png")
