import mujoco
import numpy as np

from 지시수행 import 장면_읽기
from 지시장면 import 그릇_중심, 물체들, 장면_xml, 찍기
from 찾기도구 import 개방어휘검출기

모델 = mujoco.MjModel.from_xml_string(장면_xml())
데이터 = mujoco.MjData(모델)
컬러, 깊이 = 찍기(모델, 데이터)
장면 = 장면_읽기(모델, 데이터, 개방어휘검출기(), 컬러, 깊이)

for 이름, 잰 in 장면.items():
    참_위치 = np.array(물체들[이름][3] if 이름 in 물체들 else 그릇_중심)
    오차_mm = np.linalg.norm(잰["중심"][:2] - 참_위치) * 1000
    print(f"{이름}: 가운데 ({잰['중심'][0]:.3f}, {잰['중심'][1]:.3f}) 오차 {오차_mm:4.1f}mm, "
          f"길이 {잰['길이'] * 100:4.1f} 폭 {잰['폭'] * 100:4.1f} 높이 {잰['높이'] * 100:3.1f}cm, 요 {잰['요_도']:6.1f}도")
