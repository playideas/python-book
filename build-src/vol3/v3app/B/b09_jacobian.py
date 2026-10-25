import numpy as np

L1, L2 = 0.3, 0.25                              # 2링크 평면 팔의 링크 길이(m)


def 손끝(q: np.ndarray) -> np.ndarray:
    return np.array([L1 * np.cos(q[0]) + L2 * np.cos(q[0] + q[1]),
                     L1 * np.sin(q[0]) + L2 * np.sin(q[0] + q[1])])


def 수치_야코비안(f, q: np.ndarray, h: float = 1e-6) -> np.ndarray:
    """열 i = 관절 i만 조금 움직였을 때 손끝이 움직인 비율(중앙 차분)."""
    return np.column_stack([(f(q + h * e) - f(q - h * e)) / (2 * h) for e in np.eye(len(q))])


q = np.deg2rad([30.0, 45.0])
J = 수치_야코비안(손끝, q)
s1, s12, c1, c12 = np.sin(q[0]), np.sin(q.sum()), np.cos(q[0]), np.cos(q.sum())
J_식 = np.array([[-L1 * s1 - L2 * s12, -L2 * s12], [L1 * c1 + L2 * c12, L2 * c12]])
print("수치 야코비안 == 식 ?", np.allclose(J, J_식, atol=1e-8))
print("관절 속도 [1, 0] rad/s → 손끝 속도", np.round(J @ [1.0, 0.0], 4), "m/s")

# 손끝 속도를 내려면? 정사각이면 solve, 아니면 의사역행렬, 특이점 근처면 감쇠 최소제곱(DLS)
v = np.array([0.0, 0.1])
λ = 0.01
for 이름, 각 in [("보통 자세", [30.0, 45.0]), ("거의 편 자세", [30.0, 1.0])]:
    J = 수치_야코비안(손끝, np.deg2rad(각))
    의사역 = np.linalg.pinv(J) @ v
    DLS = J.T @ np.linalg.solve(J @ J.T + λ**2 * np.eye(2), v)
    print(f"{이름}: 특이값 {np.round(np.linalg.svd(J, compute_uv=False), 4)}, "
          f"의사역 {np.round(의사역, 2)}, DLS {np.round(DLS, 2)} rad/s")
