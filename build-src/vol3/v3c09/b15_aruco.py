import mujoco
import numpy as np

from 비전장면 import K_만들기, T_세계_카메라, 머리_fovy, 변환, 장면_xml, 찍기
from 표식 import 자세_차이, 표식_자세, 표식_조각
from 회전도구 import 깔끔

자산, 몸체, 파일 = 표식_조각([0.5, -0.3, 0.751], 요_도=25)
모델 = mujoco.MjModel.from_xml_string(장면_xml(몸체, 자산), assets=파일)
데이터 = mujoco.MjData(모델)
컬러, _ = 찍기(모델, 데이터, "머리")

T_카메라_표식 = 표식_자세(컬러, K_만들기(머리_fovy))
표식 = 데이터.body("표식")
T_세계_표식 = 변환(표식.xmat.reshape(3, 3), 표식.xpos + [0, 0, 0.001])        # 판의 윗면이 표식 좌표계
T_정답 = np.linalg.inv(T_세계_카메라(데이터, "머리")) @ T_세계_표식
print("추정 위치(카메라 기준):", 깔끔(T_카메라_표식[:3, 3]))
print("정답 위치(카메라 기준):", 깔끔(T_정답[:3, 3]))
print("추정 회전:\n", 깔끔(T_카메라_표식[:3, :3]))
위치_오차, 각도_오차 = 자세_차이(T_카메라_표식, T_정답)
print(f"오차: 위치 {위치_오차:.2f}cm, 자세 {각도_오차:.2f}도")
