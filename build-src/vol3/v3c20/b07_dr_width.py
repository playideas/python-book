from dataclasses import replace

import numpy as np

from 무작위화 import 가장_좋은_칸, 무작위_물성, 점수표
from 팔제어 import 돌려_보기
from 현실팔 import 시뮬_물성, 현실_물성

짐_든_현실 = replace(현실_물성, 끝_질량=0.85)              # 현실 역할 팔이 모르는 짐 0.3kg을 들었다
print("폭  | 고른 칸     | 현실: 평균 오차, 못 감 | 짐 든 현실: 평균 오차, 못 감")
for 폭 in [0.0, 0.5, 1.0, 2.0]:
    생성기 = np.random.default_rng(0)
    kp, kd = 가장_좋은_칸(점수표(시뮬_물성, [무작위_물성(생성기, 폭) for _ in range(20)]))
    글 = []
    for 진짜 in [현실_물성, 짐_든_현실]:
        결과 = [돌려_보기(kp, kd, 시뮬_물성, 진짜, 시드) for 시드 in range(10)]
        글.append(f"{np.mean([r[0] for r in 결과]):5.2f}도, {sum(r[1] for r in 결과):2d}/40")
    print(f"{폭:.1f} | kp={kp:3d}, kd={kd} | {글[0]:>18s} | {글[1]:>18s}")
