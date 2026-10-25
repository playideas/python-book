import mujoco

from 시각언어 import 모델_이름, 묻기, 불러오기
from 지시장면 import 장면_xml, 찍기

모델 = mujoco.MjModel.from_xml_string(장면_xml())
데이터 = mujoco.MjData(모델)
사진, _ = 찍기(모델, 데이터)

처리기, vlm = 불러오기()
print(f"{모델_이름}: 매개변수 {sum(p.numel() for p in vlm.parameters()):,}개")
답, 길이 = 묻기(처리기, vlm, 사진, "Describe this image.", 최대_토큰=80)
print(f"모델에 들어간 토큰 {길이}개(질문 글은 몇 개뿐, 나머지는 사진)")
print("답:", 답)
