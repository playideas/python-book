import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from 골격도구 import 번호
from 자세모델 import 모델_불러오기, 사진_경로, 자세_찾기, 장치_고르기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

장치 = 장치_고르기()
모델 = 모델_불러오기(장치)
이미지 = np.array(Image.open(사진_경로("athlete_1913.jpg")).convert("RGB"))
결과 = 자세_찾기(모델, 이미지, 장치)
점들 = 결과["키포인트"][0]

# 얼굴 키포인트 다섯 개(코, 눈, 귀)를 감싸는 상자를 넉넉히 키워 흐리게 한다
얼굴 = 점들[[번호[이름] for 이름 in ["코", "왼눈", "오른눈", "왼귀", "오른귀"]]]
가운데 = 얼굴.mean(axis=0)
반폭 = max(np.ptp(얼굴[:, 0]), 1.0) * 1.0                 # 귀와 귀 사이 거리만큼 좌우로
x0, x1 = int(가운데[0] - 반폭), int(가운데[0] + 반폭)
y0, y1 = int(가운데[1] - 반폭 * 1.3), int(가운데[1] + 반폭 * 1.2)
가린 = 이미지.copy()
가린[y0:y1, x0:x1] = cv2.GaussianBlur(가린[y0:y1, x0:x1], (0, 0), sigmaX=15)
print("흐리게 한 얼굴 영역(x0, y0, x1, y1):", (x0, y0, x1, y1))

# 영상 대신 키포인트만 남기면 얼마나 작아질까
키포인트_기록 = np.column_stack([점들, 결과["키포인트_점수"][0]]).astype(np.float32)
print(f"사진 한 장 {이미지.nbytes:,}바이트 → 키포인트 {키포인트_기록.nbytes}바이트")

그림, 칸들 = plt.subplots(1, 2, figsize=(6, 3.4))
for 칸, 판, 제목 in zip(칸들, [이미지, 가린], ["원본", "얼굴을 흐리게"]):
    칸.imshow(판[40:640, 230:690])
    칸.set_title(제목)
    칸.axis("off")
그림.tight_layout()
그림.savefig("blur_face.png", dpi=200)
print("저장: blur_face.png")
