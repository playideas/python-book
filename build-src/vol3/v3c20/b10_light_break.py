import matplotlib.pyplot as plt
import numpy as np

from 조명장면 import IoU, 빨강_마스크, 조명카메라

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

카메라 = 조명카메라()
조건들 = {"9장 그대로": dict(), "절반 밝기": dict(밝기=0.5), "어두운 방": dict(밝기=0.25),
        "어둡고 누런 전등 + 잡음": dict(밝기=0.25, 색조=(1.0, 0.75, 0.45), 잡음=4)}
그림, 칸들 = plt.subplots(2, 4, figsize=(10, 4.2))
for 열, (이름, 설정) in enumerate(조건들.items()):
    컬러, 정답 = 카메라.찍기(**설정)
    찾은 = 빨강_마스크(컬러, 120, 40)                       # 9장의 문턱: 채도 120, 밝기 40 이상
    print(f"{이름:14s}: 컵 픽셀 밝기(V) 가운데값 {np.median(컬러[정답].max(axis=1)):5.1f}, "
          f"찾은 픽셀 {찾은.sum():4d} / 정답 {정답.sum()}, IoU {IoU(찾은, 정답):.2f}")
    칸들[0, 열].imshow(컬러[150:350, 150:450])
    칸들[0, 열].set_title(이름, fontsize=9)
    칸들[1, 열].imshow(찾은[150:350, 150:450], cmap="gray")
    칸들[1, 열].set_title(f"9장 문턱: IoU {IoU(찾은, 정답):.2f}", fontsize=9)
for 칸 in 칸들.ravel():
    칸.axis("off")
그림.tight_layout()
그림.savefig("light_break.png", dpi=200)
print("저장: light_break.png")
