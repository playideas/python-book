import numpy as np

from 계단지표 import 계단_지표, 지표_글
from 진자장면 import 실행
from 피아이디 import PID

목표 = np.deg2rad(60)
J, kd = 0.2515, 5.7
for 주기 in [0.002, 0.01, 0.02, 0.04, 0.06, 0.08]:
    기록 = 실행(PID(kp=30, ki=30, kd=kd, 주기=주기), 목표, 시간=4.0, 주기=주기)
    print(f"주기 {주기:.3f}초({1 / 주기:4.0f}Hz, kd×주기/J = {kd * 주기 / J:.2f}): "
          + 지표_글(계단_지표(기록["시각"], 기록["각도"], 0.0, 목표)))
