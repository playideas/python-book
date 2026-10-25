import numpy as np
from scipy.spatial.transform import Rotation

from 회전도구 import Rz, 깔끔

# 축 k, 각도 θ → q = [cos(θ/2), sin(θ/2) k]  (w가 맨 앞인 [w, x, y, z] 순서)
θ = np.deg2rad(90)
q = np.array([np.cos(θ / 2), 0.0, 0.0, np.sin(θ / 2)])
r = Rotation.from_quat(q, scalar_first=True)
print("z축 90도 q [w,x,y,z]:", 깔끔(q, 4), " SciPy 기본 [x,y,z,w]:", 깔끔(r.as_quat(), 4))
print("같은 회전 행렬인가? ", np.allclose(r.as_matrix(), Rz(90)))
print("-q도 같은 자세인가?  ", np.allclose(Rotation.from_quat(-q, scalar_first=True).as_matrix(), Rz(90)))

# 합치기는 곱하기, 되돌리기는 켤레(단위 쿼터니언의 역)
r30 = Rotation.from_euler("z", 30, degrees=True)
print("z 90도 다음 z 30도   :", 깔끔((r30 * r).as_euler("xyz", degrees=True)), "도")
print("r * r의 역            :", 깔끔((r * r.inv()).as_quat(scalar_first=True)))

# 두 자세 사이 각도 = 2 arccos(|q1·q2|)
q2 = r30.as_quat(scalar_first=True)
print(f"두 자세 사이 각도    : {np.rad2deg(2 * np.arccos(abs(q @ q2))):.1f}도")
