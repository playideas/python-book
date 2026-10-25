import numpy as np

# A x = b 풀기: inv(A) @ b 대신 solve를 쓴다(더 정확하고 빠르다)
A = np.array([[4.0, 1.0], [2.0, 3.0]])
b = np.array([1.0, 2.0])
x = np.linalg.solve(A, b)
print("x =", x, " 검산 A @ x =", A @ x)

# 거의 특이한 행렬: 조건수가 크면 b의 작은 오차가 x에서 크게 불어난다
A2 = np.array([[1.0, 1.0], [1.0, 1.0001]])
for b2 in [np.array([2.0, 2.0001]), np.array([2.0, 2.0002])]:
    print(f"b = {b2} → x = {np.round(np.linalg.solve(A2, b2), 4) + 0.0}")
print(f"조건수: {np.linalg.cond(A2):.0f}, 특이값: {np.round(np.linalg.svd(A2, compute_uv=False), 6)}")
