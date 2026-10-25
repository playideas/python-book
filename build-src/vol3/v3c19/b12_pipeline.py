import mujoco
import numpy as np

from 계획도구 import 계획_검사, 규칙_계획
from 그림도구 import 프레임격자
from 지시수행 import 계획_실행, 장면_읽기
from 지시장면 import 그릇_반지름, 그릇_중심, 장면_xml, 찍기
from 찾기도구 import 개방어휘검출기

지시 = "빨간 상자를 파란 그릇에 넣어 줘"
모델 = mujoco.MjModel.from_xml_string(장면_xml())
데이터 = mujoco.MjData(모델)

장면 = 장면_읽기(모델, 데이터, 개방어휘검출기(), *찍기(모델, 데이터))     # ① 보고 찾고 재기
계획 = 규칙_계획(지시, list(장면))                                     # ② 말 → 계획
문제들 = 계획_검사(계획, 장면)                                         # ③ 검사
print("계획:", " → ".join(f"{단계['기술']}({단계['대상']})" for 단계 in 계획), "/ 검사:", 문제들 or "통과")

카메라 = mujoco.MjvCamera()
카메라.lookat[:], 카메라.distance, 카메라.azimuth, 카메라.elevation = [0.38, -0.05, 0.45], 1.1, 150, -32
프레임들, 제목들 = [], []
with mujoco.Renderer(모델, 300, 400) as 그리개:
    def 사진(작업) -> None:
        """단계가 바뀔 때마다 한 장씩 찍는다."""
        if not 제목들 or 제목들[-1] != 작업.단계.value:
            그리개.update_scene(데이터, camera=카메라)
            프레임들.append(그리개.render())
            제목들.append(작업.단계.value)

    if not 문제들:                                                     # ④ 통과한 계획만 실행
        결과 = 계획_실행(모델, 데이터, 계획, 장면, 찍기=사진)
        print("실행:", 결과)
상자 = 데이터.body("빨간 상자").xpos
print(f"빨간 상자: ({상자[0]:.3f}, {상자[1]:.3f}, {상자[2]:.3f}), 그릇 가운데에서 "
      f"{np.linalg.norm(상자[:2] - 그릇_중심) * 1000:.1f}mm, 그릇 안? {np.linalg.norm(상자[:2] - 그릇_중심) < 그릇_반지름}")
고른 = [제목들.index(이름) for 이름 in ["접근", "내려가기", "들기", "옮기기", "놓기", "완료"]]
프레임격자([프레임들[i] for i in 고른], [제목들[i] for i in 고른], "pipeline.png")
print("저장: pipeline.png")
