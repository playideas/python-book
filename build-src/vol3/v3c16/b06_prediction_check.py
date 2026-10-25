import numpy as np

from MPC도구 import 예측행렬
from 이중적분기 import A, B, 굴리기

N = 4
Φ, Γ = 예측행렬(A, B, N)
print("Φ (8×2) 위 네 줄:\n", Φ[:4])
print("Γ (8×4) 위 네 줄:\n", Γ[:4])

x0 = np.array([-1.0, 0.5])
U = np.array([1.0, -0.5, 0.2, 0.0])
한꺼번에 = (Φ @ x0 + Γ @ U).reshape(N, 2)            # 행렬 곱 한 번으로 N걸음을 내다본다
하나씩 = 굴리기(x0, U)[1:]                            # 한 걸음씩 굴린 것
print("두 예측이 같은가?", np.allclose(한꺼번에, 하나씩))
