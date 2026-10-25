import matplotlib.pyplot as plt
import numpy as np

from 골격도구 import 번호, 뼈, 뼈_색
from 사람모델 import 키포인트_3d

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

도 = np.deg2rad
자세들 = {"차렷": 키포인트_3d(),
        "손 흔들기": 키포인트_3d(오른팔_각=[도(120), 0, 도(-90), 도(60)], 왼팔_각=[도(10), 0, 0, 도(20)])}
그림 = plt.figure(figsize=(7, 4.2))
for k, (제목, 점들) in enumerate(자세들.items()):
    칸 = 그림.add_subplot(1, 2, k + 1, projection="3d")
    for 가, 나 in 뼈:
        선 = 점들[[번호[가], 번호[나]]]
        칸.plot(선[:, 0], 선[:, 1], 선[:, 2], color=뼈_색(가, 나), linewidth=2.5)
    칸.scatter(점들[:, 0], 점들[:, 1], 점들[:, 2], color="black", s=8)
    # 바닥 눈금은 지우고 높이(m)만 남긴다
    칸.set(title=제목, xlim=(-0.5, 0.5), ylim=(-0.5, 0.5), zlim=(0, 1.9), xticks=[], yticks=[])
    칸.set_box_aspect((1, 1, 1.9))
    칸.view_init(elev=12, azim=30)
그림.tight_layout()
그림.savefig("body3d.png", dpi=200)
print("저장: body3d.png")
print("손 흔들기 오른손목(m):", np.round(자세들["손 흔들기"][번호["오른손목"]], 3) + 0.0)
