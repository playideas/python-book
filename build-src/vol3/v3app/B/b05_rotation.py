import numpy as np
from scipy.spatial.transform import Rotation

from 회전도구 import Rx, Ry, Rz, 깔끔

롤, 피치, 요 = 10, 20, 30                                   # 도
R = Rz(요) @ Ry(피치) @ Rx(롤)                               # 로봇 분야의 롤·피치·요(ROS, URDF rpy)
print("SciPy 'xyz'(고정 축)와 같은가?    ", np.allclose(R, Rotation.from_euler("xyz", [롤, 피치, 요], degrees=True).as_matrix()))
print("SciPy 'ZYX'(움직이는 축)와 같은가?", np.allclose(R, Rotation.from_euler("ZYX", [요, 피치, 롤], degrees=True).as_matrix()))

# 축-각(로드리게스): R = I + sinθ K + (1 - cosθ) K²,  K는 단위 축 k의 외적 행렬
k, θ = np.array([0.0, 0.0, 1.0]), np.deg2rad(30)
K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
print("로드리게스 == Rz(30) :", np.allclose(np.eye(3) + np.sin(θ) * K + (1 - np.cos(θ)) * K @ K, Rz(30)))

# 회전 행렬 → 축과 각도: 각도 = arccos((대각합 - 1) / 2)
회전벡터 = Rotation.from_matrix(R).as_rotvec()
print(f"R의 각도: {np.rad2deg(np.arccos((np.trace(R) - 1) / 2)):.3f}도, "
      f"회전 벡터 길이: {np.rad2deg(np.linalg.norm(회전벡터)):.3f}도, 축: {깔끔(회전벡터 / np.linalg.norm(회전벡터))}")
