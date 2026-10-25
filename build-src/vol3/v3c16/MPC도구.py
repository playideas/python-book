"""16장: 선형 모델 x[k+1] = A x[k] + B u[k]의 MPC. 입력 한계와 위치 상한을 다룬다."""
import numpy as np
from scipy.optimize import minimize


def 예측행렬(A: np.ndarray, B: np.ndarray, N: int) -> tuple[np.ndarray, np.ndarray]:
    """N걸음 뒤까지의 상태를 한 줄로 쌓은 X = Φ x0 + Γ U의 Φ와 Γ."""
    n, m = B.shape
    Φ = np.zeros((N * n, n))
    Γ = np.zeros((N * n, N * m))
    거듭 = np.eye(n)
    for k in range(N):
        거듭 = A @ 거듭                                   # A^(k+1)
        Φ[k * n:(k + 1) * n] = 거듭
        for j in range(k + 1):                            # u[j]가 x[k+1]에 주는 영향 A^(k-j) B
            Γ[k * n:(k + 1) * n, j * m:(j + 1) * m] = np.linalg.matrix_power(A, k - j) @ B
    return Φ, Γ


class 선형MPC:
    """비용 Σ x'Qx + u'Ru (마지막 상태는 P)를 N걸음 앞까지 최소로 하는 입력열을 매 주기 푼다."""

    def __init__(self, A: np.ndarray, B: np.ndarray, Q: np.ndarray, R: float, P: np.ndarray, N: int,
                 입력_한계: float | None = None, 위치_상한: float | None = None):
        self.N, self.입력_한계, self.위치_상한 = N, 입력_한계, 위치_상한
        self.Φ, self.Γ = 예측행렬(A, B, N)
        Q막대 = np.kron(np.eye(N), Q)
        Q막대[-2:, -2:] = P                               # 마지막 상태에는 P를 쓴다
        self.ΓᵀQ = self.Γ.T @ Q막대
        self.H = self.ΓᵀQ @ self.Γ + R * np.eye(N)        # 비용 = U'HU + 2f'U + 상수
        self.위치_고르기 = np.kron(np.eye(N), [1.0, 0.0])  # 쌓인 상태에서 위치만 뽑는다
        self.지난_답, self.성공 = np.zeros(N), True

    def 풀기(self, x0: np.ndarray) -> np.ndarray:
        """지금 상태 x0에서 앞으로 N개의 입력을 돌려준다(첫 값만 쓸 것)."""
        f = self.ΓᵀQ @ (self.Φ @ x0)
        if self.입력_한계 is None and self.위치_상한 is None:
            return np.linalg.solve(self.H, -f)            # 제약이 없으면 한 번에 풀린다
        제약 = []
        if self.위치_상한 is not None:                    # 상한 - 예측 위치 ≥ 0
            S = self.위치_고르기
            제약.append({"type": "ineq",
                       "fun": lambda U: self.위치_상한 - S @ (self.Φ @ x0 + self.Γ @ U),
                       "jac": lambda U: -S @ self.Γ})
        한계 = None if self.입력_한계 is None else [(-self.입력_한계, self.입력_한계)] * self.N
        첫_추측 = np.r_[self.지난_답[1:], self.지난_답[-1]]   # 지난 답을 한 칸 당겨 시작점으로
        결과 = minimize(lambda U: U @ self.H @ U + 2 * f @ U, 첫_추측,
                      jac=lambda U: 2 * (self.H @ U + f), bounds=한계, constraints=제약,
                      method="SLSQP", options={"maxiter": 200, "ftol": 1e-9})
        self.지난_답, self.성공 = 결과.x, bool(결과.success)
        return 결과.x
