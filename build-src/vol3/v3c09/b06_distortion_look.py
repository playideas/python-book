import cv2
import matplotlib.pyplot as plt
import numpy as np

from 체커보드 import K_참, 보드_사진들, 왜곡_참

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

반듯한 = 보드_사진들(1, 퍼짐=0, 거리=(0.34, 0.34), 왜곡=False)[0]          # 왜곡 없는 이상적인 카메라
휜 = 보드_사진들(1, 퍼짐=0, 거리=(0.34, 0.34), 왜곡=True)[0]              # 같은 자세, 왜곡 있는 렌즈
편 = cv2.undistort(휜, K_참, 왜곡_참)                     # 왜곡 계수를 알면 되돌릴 수 있다

# 왜곡 때문에 픽셀이 얼마나 밀려나나: 같은 방향의 빛이 이상적인 카메라와 진짜 렌즈에서 찍히는 곳
v, u = np.mgrid[0:480:20, 0:640:20]
방향 = np.stack([(u.ravel() - K_참[0, 2]) / K_참[0, 0], (v.ravel() - K_참[1, 2]) / K_참[1, 1],
                np.ones(u.size)], axis=1)
진짜, _ = cv2.projectPoints(방향, np.zeros(3), np.zeros(3), K_참, 왜곡_참)
밀림 = np.linalg.norm(진짜.reshape(-1, 2) - np.stack([u.ravel(), v.ravel()], axis=1), axis=1)
가운데_거리 = np.hypot(u.ravel() - K_참[0, 2], v.ravel() - K_참[1, 2])
for 반경 in [100, 200, 300, 390]:
    print(f"가운데에서 {반경:3d}px 안쪽: 가장 많이 밀린 픽셀 {밀림[가운데_거리 <= 반경].max():5.1f}px")

그림, 칸들 = plt.subplots(1, 3, figsize=(10, 2.9))
for 칸, 사진, 제목 in zip(칸들, [반듯한, 휜, 편], ["이상적인 카메라", "왜곡 있는 렌즈", "왜곡을 되돌린 사진"]):
    칸.imshow(사진)
    칸.set_title(제목, fontsize=10)
    칸.axis("off")
그림.tight_layout()
그림.savefig("distortion.png", dpi=200)
print("저장: distortion.png")
