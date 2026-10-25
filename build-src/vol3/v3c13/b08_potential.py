import numpy as np

from 디귿장면 import 목표, 시작, 벽까지
from 점로봇 import 속도_제한
from 퍼텐셜 import 내리막, 퍼텐셜

주기 = 0.01                                           # 벽 근처는 비탈이 가팔라서 잘게 걷는다
위치 = 시작.copy()
for _ in range(6000):                                 # 60초 동안 내리막을 따라 굴러간다
    위치 = 위치 + 속도_제한(내리막(위치)) * 주기
print(f"60초 뒤 위치 {np.round(위치, 3)}, 목표까지 {np.linalg.norm(목표 - 위치):.3f}m, "
      f"벽까지 {벽까지(위치)[0]:.3f}m")
print(f"그 자리의 내리막 세기 {np.linalg.norm(내리막(위치)):.6f}")

# 그 자리가 정말 '우묵한 곳'인지: 둘레 1cm 여덟 방향의 높이와 견준다
둘레 = [위치 + 0.01 * np.array([np.cos(a), np.sin(a)]) for a in np.linspace(0, 2 * np.pi, 8, endpoint=False)]
print(f"높이: 그 자리 {퍼텐셜(위치):.5f}, 둘레 1cm 중 가장 낮은 곳 {min(퍼텐셜(p) for p in 둘레):.5f}")
print("둘레 여덟 곳이 모두 더 높은가?", all(퍼텐셜(p) > 퍼텐셜(위치) for p in 둘레))
print(f"높이: 목표 {퍼텐셜(목표):.5f}")
