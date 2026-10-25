import mujoco
import numpy as np

from 계획도구 import 규칙_계획
from 시각언어 import 묻기, 불러오기
from 지시수행 import 계획_실행, 장면_읽기
from 지시장면 import 그릇_반지름, 그릇_중심, 장면_xml, 찍기
from 찾기도구 import 개방어휘검출기

모델 = mujoco.MjModel.from_xml_string(장면_xml())
데이터 = mujoco.MjData(모델)
검출기 = 개방어휘검출기()
처리기, vlm = 불러오기()
질문들 = ["Is the red box inside the blue bowl? Answer yes or no.",
         "Is the green box inside the blue bowl? Answer yes or no."]


def 확인(때: str) -> None:
    """지금 장면을 찍어 VLM에게 묻고, 시뮬레이터가 아는 정답과 나란히 적는다."""
    사진, _ = 찍기(모델, 데이터)
    for 질문, 이름 in zip(질문들, ["빨간 상자", "초록 상자"]):
        정답 = np.linalg.norm(데이터.body(이름).xpos[:2] - 그릇_중심) < 그릇_반지름
        print(f"[{때}] {질문.split('?')[0]}? → VLM {묻기(처리기, vlm, 사진, 질문, 5)[0]!r}, 정답 {'Yes' if 정답 else 'No'}")


확인("옮기기 전")
장면 = 장면_읽기(모델, 데이터, 검출기, *찍기(모델, 데이터))
계획_실행(모델, 데이터, 규칙_계획("빨간 상자를 파란 그릇에 넣어 줘", list(장면)), 장면)
확인("옮긴 뒤")

# 같은 확인을 검출기와 깊이로: 다시 찍어 빨간 상자를 재고, 옮기기 전에 잰 그릇 가운데와 비교한다
뒤 = 장면_읽기(모델, 데이터, 검출기, *찍기(모델, 데이터))
거리 = np.linalg.norm(뒤["빨간 상자"]["중심"][:2] - 장면["파란 그릇"]["중심"][:2])
print(f"[옮긴 뒤] 잰 빨간 상자와 그릇 가운데 거리 {거리 * 1000:.1f}mm → 그릇 안? {거리 < 그릇_반지름}"
      f" (점수 {뒤['빨간 상자']['점수']:.2f})")
