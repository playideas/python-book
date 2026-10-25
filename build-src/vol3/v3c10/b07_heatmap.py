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

# 키포인트 머리의 마지막 층이 내놓는 히트맵을 갈고리(hook)로 받아 둔다
담기 = {}
모델.roi_heads.keypoint_predictor.register_forward_hook(lambda 층, 입력, 출력: 담기.update(히트맵=출력))
이미지 = np.array(Image.open(사진_경로("athlete_1913.jpg")).convert("RGB"))
결과 = 자세_찾기(모델, 이미지, 장치)
히트맵 = 담기["히트맵"][0].cpu().numpy()          # 1번 사람: (17, 56, 56)
print("히트맵 모양:", 히트맵.shape)

x0, y0, x1, y1 = np.round(결과["상자"][0]).astype(int)
상자_안 = 이미지[y0:y1, x0:x1]
그림, 칸들 = plt.subplots(1, 4, figsize=(7, 5.6))
칸들[0].imshow(상자_안)
칸들[0].set_title("상자 안")
for 칸, 이름 in zip(칸들[1:], ["코", "오른손목", "왼발목"]):
    맵 = 히트맵[번호[이름]]
    칸.imshow(상자_안)
    칸.imshow(cv2.resize(맵, (x1 - x0, y1 - y0)), cmap="magma", alpha=0.6)   # 56×56을 상자 크기로 늘려 겹친다
    칸.set_title(이름)
    높은_칸 = int((맵 > 맵.max() / 2).sum())
    print(f"{이름}: 가장 높은 값 {맵.max():.1f}, 그 절반을 넘는 칸 {높은_칸}개, 최종 점수 {결과['키포인트_점수'][0, 번호[이름]]:.1f}")
for 칸 in 칸들:
    칸.axis("off")
그림.tight_layout()
그림.savefig("heatmaps.png", dpi=200)
print("저장: heatmaps.png")
