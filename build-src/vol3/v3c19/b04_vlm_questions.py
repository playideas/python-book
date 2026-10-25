import mujoco

from 시각언어 import 묻기, 불러오기
from 지시장면 import 장면_xml, 찍기

모델 = mujoco.MjModel.from_xml_string(장면_xml())
데이터 = mujoco.MjData(모델)
사진, _ = 찍기(모델, 데이터)
처리기, vlm = 불러오기()

질문들 = [
    "Is there a red box on the table? Answer yes or no.",       # 있다
    "Is there a banana on the table? Answer yes or no.",        # 없다
    "What color is the bowl?",                                  # 파랑
    "How many red objects are on the table?",                   # 둘(상자와 공)
    "Is the red box to the left or to the right of the green box?",   # 사진에서 오른쪽
    "Where is the blue bowl in the image? Give pixel coordinates.",
    "탁자 위에 무엇이 있나요?",
]
for 질문 in 질문들:
    답, _ = 묻기(처리기, vlm, 사진, 질문, 최대_토큰=40)
    print(f"Q: {질문}\nA: {답}")
