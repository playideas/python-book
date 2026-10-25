import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from 골격도구 import 골격_그리기
from 자세모델 import 모델_불러오기, 사진_경로, 자세_찾기, 장치_고르기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

사람_문턱 = 0.9              # 사람 상자 점수가 이보다 낮으면 버린다
키포인트_문턱 = 2.0          # 키포인트 점수가 이보다 낮으면 그리지 않는다

장치 = 장치_고르기()
모델 = 모델_불러오기(장치)
그림, 칸들 = plt.subplots(1, 2, figsize=(8, 3.9), gridspec_kw={"width_ratios": [0.73, 1.36]})
for 칸, 파일 in zip(칸들, ["athlete_1913.jpg", "runners_1912.jpg"]):
    이미지 = np.array(Image.open(사진_경로(파일)).convert("RGB"))
    결과 = 자세_찾기(모델, 이미지, 장치)
    칸.imshow(이미지)
    for 상자, 점수, 점들, 점_점수 in zip(결과["상자"], 결과["점수"], 결과["키포인트"], 결과["키포인트_점수"]):
        if 점수 < 사람_문턱:
            continue
        골격_그리기(칸, 점들, 보임=점_점수 > 키포인트_문턱, 굵기=1.8)
        x0, y0, x1, y1 = 상자
        칸.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, color="lime", linewidth=1))
        print(f"{파일}: 상자 높이 {y1 - y0:4.0f}px, 사람 점수 {점수:.3f}, "
              f"문턱을 넘은 키포인트 {int((점_점수 > 키포인트_문턱).sum()):2d}개")
    칸.axis("off")
그림.tight_layout()
그림.savefig("photo_pose.png", dpi=200)
print("저장: photo_pose.png")
