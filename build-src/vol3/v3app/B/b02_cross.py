import numpy as np

x, y, z = np.eye(3)
print("x × y =", np.cross(x, y), "  y × x =", np.cross(y, x))

# 3장 야코비안의 한 열: 축 방향 z로 도는 관절, 관절에서 손끝까지의 화살표 r
축 = np.array([0.0, 0.0, 1.0])
r = np.array([0.3, 0.0, 0.0])                  # 손끝이 관절에서 x 방향으로 0.3m
각속도 = 2.0                                     # rad/s
print("손끝 속도 = ω (축 × r) =", 각속도 * np.cross(축, r), "m/s")

# 외적의 길이 = 두 벡터가 만드는 평행사변형 넓이, 방향은 두 벡터에 모두 수직
a, b = np.array([2.0, 0.0, 0.0]), np.array([1.0, 3.0, 0.0])
n = np.cross(a, b)
print("a × b =", n, " 넓이:", np.linalg.norm(n), " a·n, b·n:", a @ n, b @ n)
