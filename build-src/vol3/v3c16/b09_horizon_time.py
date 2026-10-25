import time

import numpy as np

from LQR도구 import LQR
from MPC도구 import 선형MPC
from 이중적분기 import A, B, 주기

Q, R = np.diag([1.0, 0.1]), 0.01
_, P = LQR(A, B, Q, R)
print(f"제어 주기 {주기 * 1000:.0f}ms 안에 풀어야 한다")
for N in [5, 10, 20, 40, 80, 160]:
    mpc = 선형MPC(A, B, Q, R, P, N, 입력_한계=1.0, 위치_상한=0.05)
    x, 가장_멀리, 실패, 걸린_시간 = np.array([-2.0, 1.0]), -2.0, 0, []
    for _ in range(80):
        시작 = time.perf_counter()
        u = mpc.풀기(x)[0]
        걸린_시간.append(time.perf_counter() - 시작)
        실패 += not mpc.성공                      # 제약을 다 지키는 답을 못 찾은 주기
        x = A @ x + B[:, 0] * np.clip(u, -1, 1)
        가장_멀리 = max(가장_멀리, x[0])
    걸린_시간 = np.array(걸린_시간) * 1000
    print(f"N={N:3d}({N * 주기:4.1f}초): 가장 멀리 {가장_멀리 * 100:4.1f}cm, 못 푼 주기 {실패:2d} | "
          f"첫 주기 {걸린_시간[0]:5.1f}ms, 그 뒤 중앙값 {np.median(걸린_시간[1:]):.2f}ms, 최대 {걸린_시간[1:].max():4.1f}ms")
