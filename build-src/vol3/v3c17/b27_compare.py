import time

import numpy as np
import torch

from MPPI도구 import MPPI
from PPO도구 import 행위자비평가
from 진자장면 import 토크_한계
from 진자흔들기환경 import 진자흔들기환경
from 흔들기시험 import 시험, 평균_행동

모델 = 행위자비평가(3, 1)                                  # 같은 설계도를 먼저 만들고
모델.load_state_dict(torch.load("흔들기_정책.pt", weights_only=True))   # 숫자를 채운다
환경 = 진자흔들기환경()
제어기 = MPPI(환경.모델, 후보_수=128, 걸음_수=100)          # 16장과 같은 설정
학습한_정책 = 평균_행동(모델)
걸린_시간 = {"PPO": [], "MPPI": []}


def PPO_정책(상태: np.ndarray) -> np.ndarray:
    시작 = time.perf_counter()
    행동 = 학습한_정책(상태)
    걸린_시간["PPO"].append(time.perf_counter() - 시작)
    return 행동


def MPPI_정책(상태: np.ndarray) -> np.ndarray:
    if 환경.걸음 == 0:
        제어기.계획[:] = 0.0                               # 새 판이면 지난 판의 계획을 버린다
    시작 = time.perf_counter()
    토크 = 제어기.고르기(환경.데이터)                      # 관측 대신 MuJoCo 상태를 통째로 본다
    걸린_시간["MPPI"].append(time.perf_counter() - 시작)
    return np.array([토크 / 토크_한계])


print(f"{'방법':5s} {'성공률':>5s} {'올라선 시각(평균, 범위)':>22s} {'한 번 고르는 시간(중앙값)':>18s}")
for 이름, 정책 in [("PPO", PPO_정책), ("MPPI", MPPI_정책)]:
    결과 = 시험(환경, 정책, 판_수=20)
    시각 = 결과["올라선_시각"]
    print(f"{이름:5s} {결과['성공률']:6.0%}   {np.mean(시각):.2f}초 ({min(시각):.2f}~{max(시각):.2f}초)"
          f"   {np.median(걸린_시간[이름]) * 1000:8.3f}ms")
