import numpy as np

rng = np.random.default_rng(0)
P = np.array([[0.04, 0.03],                    # x, y 위치의 공분산(m²)
              [0.03, 0.09]])                    # 대각은 분산, 바깥은 함께 흔들리는 정도
점들 = rng.multivariate_normal([0.0, 0.0], P, size=50_000)
print("표본 공분산 np.cov:\n", np.round(np.cov(점들.T), 4))
print(f"상관 계수: {P[0, 1] / np.sqrt(P[0, 0] * P[1, 1]):.3f}")

# 타원의 축: 고유값의 제곱근이 축 길이(표준편차), 고유벡터가 방향
고유값, 고유벡터 = np.linalg.eigh(P)
print("축 길이 1σ:", np.round(np.sqrt(고유값), 4), " 긴 축 방향:", np.round(고유벡터[:, 1], 4))

# 선형 변환 y = A x 를 거치면 공분산은 A P Aᵀ (칼만 필터의 예측 단계)
A = np.array([[1.0, 0.1], [0.0, 1.0]])
print("A P Aᵀ:\n", np.round(A @ P @ A.T, 4))
print("옮긴 점들의 공분산:\n", np.round(np.cov((점들 @ A.T).T), 4))
