import numpy as np
from PIL import Image

from 골격도구 import 키포인트_이름
from 자세모델 import 모델_불러오기, 사진_경로, 자세_찾기, 장치_고르기

장치 = 장치_고르기()
모델 = 모델_불러오기(장치)
이미지 = np.array(Image.open(사진_경로("athlete_1913.jpg")).convert("RGB"))
print("장치:", 장치, "/ 이미지:", 이미지.shape)

결과 = 자세_찾기(모델, 이미지, 장치)
print("찾은 사람 후보:", len(결과["점수"]), "명, 점수", np.round(결과["점수"], 3))
print("1번 사람 상자(x0, y0, x1, y1):", np.round(결과["상자"][0]).astype(int))
for i in range(0, 17, 3):
    print("  ".join(f"{키포인트_이름[j]} ({결과['키포인트'][0, j, 0]:.0f}, {결과['키포인트'][0, j, 1]:.0f}) "
                    f"{결과['키포인트_점수'][0, j]:.1f}" for j in range(i, min(i + 3, 17))))
