import numpy as np
from scipy.linalg import solve_discrete_are

from 이중적분기 import A, B

Q = np.diag([1.0, 0.1])
R = 0.1

# 1) 끝에서부터 거꾸로: 남은 걸음이 하나씩 늘 때 '앞으로 쌓일 비용' 행렬 P를 고쳐 쓴다
P = Q.copy()
for 걸음 in range(1, 201):
    K = np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A)
    P_새 = Q + A.T @ P @ (A - B @ K)
    if 걸음 in (1, 5, 20, 200):
        print(f"남은 걸음 {걸음:3d}: K = {np.round(K[0], 3)}")
    P = P_새

# 2) 끝없이 긴 구간: 리카티 방정식을 SciPy로 한 번에 푼다
P무한 = solve_discrete_are(A, B, Q, R)
K무한 = np.linalg.solve(R + B.T @ P무한 @ B, B.T @ P무한 @ A)
print("SciPy 리카티 풀이 K =", np.round(K무한[0], 3))
print("닫힌 고리 A - BK의 고유값 크기:", np.round(np.abs(np.linalg.eigvals(A - B @ K무한)), 3))
