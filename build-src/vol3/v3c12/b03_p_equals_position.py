import mujoco
import numpy as np

from 진자장면 import XML, 실행
from 피아이디 import PID

목표 = np.deg2rad(60)
# 우리 P 제어기를 시뮬레이션 걸음마다(0.001초) 부르고, 토크 한계는 사실상 없앤다
우리_것 = 실행(PID(kp=20, ki=0, kd=0, 주기=0.001), 목표, 시간=3.0, 주기=0.001, 토크_한계=1e6)

# 같은 진자에 4장의 position 액추에이터(kp=20)를 단다
xml = XML.replace('<motor name="모터" joint="pivot" ctrlrange="-50 50"/>',
                  '<position name="모터" joint="pivot" kp="20"/>')
모델 = mujoco.MjModel.from_xml_string(xml)
데이터 = mujoco.MjData(모델)
데이터.ctrl[0] = 목표
위치_액추에이터 = []
for _ in range(3000):
    위치_액추에이터.append(데이터.qpos[0])
    mujoco.mj_step(모델, 데이터)

차이 = np.abs(np.array(위치_액추에이터) - 우리_것["각도"]).max()
print(f"3초 동안 두 진자 각도의 가장 큰 차이: {np.rad2deg(차이):.1e}도")
print(f"각도 범위: {np.rad2deg(우리_것['각도'].min()) + 0.0:.1f}도 ~ {np.rad2deg(우리_것['각도'].max()):.1f}도")
