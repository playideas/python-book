import numpy as np
from scipy.linalg import expm

# 이중 적분기(16장): 상태 [위치, 속도], 입력 가속도 u. 연속 시간 식은 d[위치, 속도]/dt = Ac·상태 + Bc·u
Ac = np.array([[0.0, 1.0], [0.0, 0.0]])
Bc = np.array([[0.0], [1.0]])
Δt = 0.1

# 한 주기 동안 u를 그대로 둔다면: A = exp(Ac Δt), B = ∫exp(Ac s)ds Bc. 큰 행렬 하나의 exp로 한 번에 구한다
M = expm(np.block([[Ac, Bc], [np.zeros((1, 3))]]) * Δt)
A, B = M[:2, :2], M[:2, 2:]
print("A =", A.tolist(), " B =", np.round(B.ravel(), 6).tolist())
print("손으로 쓴 식 A=[[1,Δt],[0,1]], B=[Δt²/2, Δt]와 같은가?",
      np.allclose(A, [[1, Δt], [0, 1]]) and np.allclose(B.ravel(), [Δt**2 / 2, Δt]))

# 이산 시간 PID의 적분과 미분(12장): 적분은 오차 × 주기를 더하고, 미분은 차이 ÷ 주기
오차들 = np.array([1.0, 0.8, 0.5, 0.3, 0.2])
print("적분(누적 합 × Δt):", np.round(np.cumsum(오차들) * Δt, 3), " 미분(차이 ÷ Δt):", np.round(np.diff(오차들) / Δt, 3))
