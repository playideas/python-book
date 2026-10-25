import numpy as np

from LQR도구 import LQR
from MPC도구 import 선형MPC
from 이중적분기 import A, B

Q, R = np.diag([1.0, 0.1]), 0.1
K, P = LQR(A, B, Q, R)
x0 = np.array([-1.0, 0.5])
print(f"LQR이 고른 첫 입력: {float((-K @ x0)[0]):.4f}")
for N in [1, 5, 20, 60]:
    끝_P = 선형MPC(A, B, Q, R, P, N).풀기(x0)[0]          # 마지막 상태에 리카티의 P를 쓴 MPC
    끝_Q = 선형MPC(A, B, Q, R, Q, N).풀기(x0)[0]          # 마지막 상태도 그냥 Q로 잰 MPC
    print(f"N={N:2d}: 끝 비용 P → {끝_P:.4f} | 끝 비용 Q → {끝_Q:.4f}")
