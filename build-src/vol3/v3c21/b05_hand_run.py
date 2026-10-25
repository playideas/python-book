import mujoco

from 손배치 import 손_배치
from 정리로봇 import 정리로봇
from 책상장면 import 장면_xml

모델 = mujoco.MjModel.from_xml_string(장면_xml(손_배치))
데이터 = mujoco.MjData(모델)
for 시각, 무엇, 메모 in 정리로봇(모델, 데이터).정리():
    print(f"{시각:5.1f}초  {무엇:5s} {메모}")
