import numpy as np

from 카메라도구 import 삼각측량, 카메라_만들기, 투영

손목_세계 = np.array([0.0, -0.44, 1.87])
생성기 = np.random.default_rng(0)
print("두 카메라 사이 각도 → 3D 오차 평균(mm)과 축별 흔들림(표준편차, mm)  [픽셀 잡음 2px]")
for 사이각_도 in [5, 15, 30, 60, 90, 120]:
    반 = np.deg2rad(사이각_도 / 2)
    # 사람을 중심으로 반지름 3m 원 위에, 정면(+x)에서 좌우로 반씩 벌려 놓는다
    P들 = [카메라_만들기([3 * np.cos(부호 * 반), 3 * np.sin(부호 * 반), 1.3], [0, 0, 1.2]) for 부호 in (+1, -1)]
    픽셀들 = [투영(P, 손목_세계[None])[0] for P in P들]
    복원들 = np.array([삼각측량(P들, [p + 생성기.normal(0, 2.0, 2) for p in 픽셀들]) for _ in range(1000)])
    오차 = np.linalg.norm(복원들 - 손목_세계, axis=1) * 1000
    x, y, z = 복원들.std(axis=0) * 1000
    print(f"  {사이각_도:3d}도: 평균 {오차.mean():6.1f}  앞뒤(x) {x:6.1f}  좌우(y) {y:5.1f}  위아래(z) {z:5.1f}")
