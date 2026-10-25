import numpy as np

from 두링크 import 순기구학2, 야코비안2

목표 = np.array([0.5, 0.3])

for 시작_도 in [(90.0, -30.0), (0.0, 30.0)]:
    q = np.deg2rad(시작_도)
    print(f"시작 (어깨, 팔꿈치) = {시작_도}도")
    for 반복 in range(8):
        오차 = 목표 - 순기구학2(q)                       # 손끝이 가야 할 남은 거리
        print(f"  {반복}회: 남은 거리 {np.linalg.norm(오차):.2e}m")
        if np.linalg.norm(오차) < 1e-9:
            break
        q = q + np.linalg.pinv(야코비안2(q)) @ 오차      # 직선으로 가정하고 한 걸음
    print(f"  → 어깨 {np.rad2deg(q[0]):.1f}도, 팔꿈치 {np.rad2deg(q[1]):.1f}도")
