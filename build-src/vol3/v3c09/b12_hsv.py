import cv2
import matplotlib.pyplot as plt
import mujoco
import numpy as np

from 비전장면 import 장면_xml, 찍기
from 색찾기 import 색_마스크, 색_범위

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

모델 = mujoco.MjModel.from_xml_string(장면_xml())
데이터 = mujoco.MjData(모델)
컬러, _ = 찍기(모델, 데이터, "머리")

hsv = cv2.cvtColor(컬러, cv2.COLOR_RGB2HSV)
for 이름, (행, 열) in {"빨강 컵 윗면": (230, 245), "빨강 컵 옆면": (265, 235), "공 그림자": (325, 365), "탁자": (380, 100)}.items():
    print(f"{이름:6s}: RGB {컬러[행, 열]} → HSV {hsv[행, 열]}")

그림, 칸들 = plt.subplots(1, 4, figsize=(10, 2.2))
for 칸, 이름 in zip(칸들, 색_범위):
    마스크 = 색_마스크(컬러, 이름)
    칸.imshow(마스크, cmap="gray")
    칸.set_title(f"{이름}: {np.count_nonzero(마스크)}픽셀", fontsize=10)
    칸.axis("off")
그림.tight_layout()
그림.savefig("hsv_masks.png", dpi=200)
print("저장: hsv_masks.png")
