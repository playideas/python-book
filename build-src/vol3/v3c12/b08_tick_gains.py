import numpy as np

from 계단지표 import 계단_지표, 지표_글
from 진자장면 import 실행
from 피아이디 import PID


class 박자PID:
    """주기를 곱하고 나누지 않는 PID. 이득이 '한 박자당' 값이라 주기가 바뀌면 뜻이 달라진다."""

    def __init__(self, kp: float, ki_박자: float, kd_박자: float):
        self.kp, self.ki_박자, self.kd_박자 = kp, ki_박자, kd_박자
        self.적분, self.이전_오차 = 0.0, None

    def __call__(self, 목표: float, 측정: float) -> float:
        오차 = 목표 - 측정
        self.적분 += 오차                               # 주기를 곱하지 않는다
        미분 = 0.0 if self.이전_오차 is None else 오차 - self.이전_오차   # 주기로 나누지 않는다
        self.이전_오차 = 오차
        return self.kp * 오차 + self.ki_박자 * self.적분 + self.kd_박자 * 미분


목표 = np.deg2rad(60)
kp, ki, kd = 30, 30, 5.7
# 100Hz에서 똑같이 움직이도록 맞춘 '한 박자당' 이득
ki_박자, kd_박자 = ki * 0.01, kd / 0.01
for 주기 in [0.01, 0.005]:
    for 이름, 제어기 in [("주기를 쓰는 PID", PID(kp, ki, kd, 주기)), ("박자 이득 PID ", 박자PID(kp, ki_박자, kd_박자))]:
        기록 = 실행(제어기, 목표, 시간=4.0, 주기=주기)
        print(f"{1 / 주기:3.0f}Hz {이름}: " + 지표_글(계단_지표(기록["시각"], 기록["각도"], 0.0, 목표)))
