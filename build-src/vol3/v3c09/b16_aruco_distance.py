import mujoco
import numpy as np

from 비전장면 import K_만들기, T_세계_카메라, 바라보기, 변환, 찍기, 축_글자
from 표식 import 변_길이, 자세_차이, 표식_자세, 표식_조각

자산, 몸체, 파일 = 표식_조각([0, 0, 0.001])
K = K_만들기(60)
print(" 거리 | 표식 크기 | 위치 오차 | 자세 오차")
for 거리 in [0.3, 0.6, 0.9, 1.2, 1.5]:
    위치 = 거리 * np.array([np.sin(np.deg2rad(30)), 0, np.cos(np.deg2rad(30))])   # 30도 비스듬히
    xml = f"""<mujoco><visual><global offwidth="640" offheight="480"/></visual>
      <asset>{자산}</asset><worldbody><light pos="0 0 2" dir="0 0 -1"/>
      <camera name="눈" pos="{' '.join(map(str, 위치))}" xyaxes="{축_글자(바라보기(위치, [0, 0, 0]))}" fovy="60"/>
      {몸체}</worldbody></mujoco>"""
    모델 = mujoco.MjModel.from_xml_string(xml, assets=파일)
    데이터 = mujoco.MjData(모델)
    컬러, _ = 찍기(모델, 데이터, "눈")
    T_추정 = 표식_자세(컬러, K)
    T_정답 = np.linalg.inv(T_세계_카메라(데이터, "눈")) @ 변환(np.eye(3), [0, 0, 0.002])   # 표식 윗면
    위치_오차, 각도_오차 = 자세_차이(T_추정, T_정답)
    print(f"{거리:4.1f}m | {변_길이 * K[0, 0] / 거리:6.1f}px | {위치_오차:6.2f}cm | {각도_오차:6.2f}도")
