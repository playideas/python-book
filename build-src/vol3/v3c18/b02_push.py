import mujoco
import numpy as np

from 모방환경 import 집고놓기환경, 최대_걸음
from 전문가 import 목표_정하기, 전문가

환경 = 집고놓기환경([0.45, 0.15])
상자_주소 = 환경.모델.jnt_qposadr[환경.모델.body("box").jntadr[0]]    # 상자 자유 관절의 qpos 시작 칸
기록 = []
while 환경.걸음 < 최대_걸음 and not 환경.끝났나():
    if 환경.걸음 == 50:                                  # 내려가는 도중에 누가 상자를 5cm 옮겨 놓는다
        환경.데이터.qpos[상자_주소:상자_주소 + 2] += [-0.03, 0.04]
        mujoco.mj_forward(환경.모델, 환경.데이터)
        print("50걸음: 상자를 옮겼다 →", np.round(환경.데이터.body("box").xpos[:2], 3))
    단계 = 목표_정하기(환경)[2]
    if not 기록 or 기록[-1][1] != 단계:
        기록.append((환경.걸음, 단계))
    환경.한걸음(전문가(환경))
print("단계 변화:", ", ".join(f"{걸음} {단계}" for 걸음, 단계 in 기록))
print(f"끝: {환경.걸음}걸음, 성공 {환경.성공()}")
