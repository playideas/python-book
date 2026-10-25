import numpy as np

from 회전도구 import Rz, 깔끔

A = np.array([[1.0, 2.0], [3.0, 4.0]])
B = np.array([[0.0, 1.0], [1.0, 0.0]])
print("A @ B =\n", A @ B)
print("B @ A =\n", B @ A)                         # 순서를 바꾸면 결과가 다르다
print("(A @ B).T == B.T @ A.T ?", np.allclose((A @ B).T, B.T @ A.T))
print("행렬식 det(A) =", round(np.linalg.det(A), 6))
print("A의 역행렬 =\n", np.linalg.inv(A))

R = Rz(30)
print("회전 행렬의 역 = 전치 ?", np.allclose(np.linalg.inv(R), R.T), " det(R) =", 깔끔(np.linalg.det(R)))
