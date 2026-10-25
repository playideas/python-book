import mujoco

from 지시장면 import 장면_xml, 찍기
from 찾기도구 import 개방어휘검출기

모델 = mujoco.MjModel.from_xml_string(장면_xml())
데이터 = mujoco.MjData(모델)
사진, _ = 찍기(모델, 데이터)
검출기 = 개방어휘검출기()

# 장면에 없는 것, 뭉뚱그린 말, 한국어를 하나씩 따로 묻는다. 문턱을 0.02로 낮춰 약한 답도 본다
for 글 in ["a banana", "a robot", "a cup", "a box", "a ball", "a red cube", "빨간 상자"]:
    찾은것 = 검출기.찾기(사진, [글], 문턱=0.02)
    if 글 in 찾은것:
        점수, (x1, y1, x2, y2) = 찾은것[글]
        print(f"{글:11s} → 점수 {점수:.2f}, 상자 x {x1:.0f}~{x2:.0f}, y {y1:.0f}~{y2:.0f}")
    else:
        print(f"{글:11s} → 0.02 넘는 상자 없음")
