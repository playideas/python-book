"""20장: 세로 팔의 관절별 PID(12장 실전PID) + 중력 앞먹임, 그리고 성적 매기기."""
from collections.abc import Callable

import numpy as np

from 실전PID import 실전PID
from 현실팔 import 물성, 실행, 주기, 중력_토크, 토크_한계

목표들 = np.deg2rad([[-30, 60], [20, 40], [45, -45], [-60, 30]])   # (어깨, 팔꿈치), 12장 실습과 같다
머무름 = 2.0                                                         # 목표 하나에 머무는 시간(초)


def 목표(t: float) -> np.ndarray:
    return 목표들[min(int(t // 머무름), len(목표들) - 1)]


def 제어기_만들기(kp: float, kd: float, 아는: 물성, 목표함수: Callable = 목표) -> Callable:
    """어깨 이득 (kp, kd)를 받아 팔꿈치는 12장처럼 kp×0.375, kd×0.25로 둔다. ki = kp, 적분 분리 10도.

    아는 물성으로 중력 앞먹임을 계산하고, 모터가 약하다고 알고 있으면 그만큼 크게 명령한다.
    """
    pid들 = [실전PID(kp * 배율_p, kp * 배율_p, kd * 배율_d, 주기, 출력_한계=한계, 적분_구간=np.deg2rad(10))
            for 배율_p, 배율_d, 한계 in [(1, 1, 토크_한계[0]), (0.375, 0.25, 토크_한계[1])]]
    중력 = 중력_토크(아는)

    def 제어기(t: float, 잰_각도: np.ndarray) -> np.ndarray:
        앞먹임 = 중력(잰_각도)
        목표값 = 목표함수(t)
        토크 = np.array([pid(목표값[i], 잰_각도[i], 앞먹임[i]) for i, pid in enumerate(pid들)])
        return 토크 / 아는.토크_배율
    return 제어기


def 성적(기록: dict) -> tuple[float, int]:
    """링크의 참 각도로 매긴 평균 오차(도)와, 머무름이 끝날 때 ±2도 밖에 있던 목표 수."""
    목표값 = np.array([목표(t) for t in 기록["시각"]])
    오차_도 = np.rad2deg(np.abs(목표값 - 기록["참_각도"]))
    n = round(머무름 / 주기)
    못_감 = sum(int(오차_도[(i + 1) * n - 1].max() > 2.0) for i in range(len(목표들)))
    return float(오차_도.mean()), 못_감


def 돌려_보기(kp: float, kd: float, 아는: 물성, 진짜: 물성, 시드: int = 0) -> tuple[float, int]:
    """아는 물성으로 만든 제어기를 진짜 물성의 팔에서 돌려 성적을 낸다."""
    return 성적(실행(제어기_만들기(kp, kd, 아는), 머무름 * len(목표들), 진짜, 시드))
