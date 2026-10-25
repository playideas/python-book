import numpy as np

from 팔공간 import 상한, 선분_충돌, 하한
from 표본계획 import RRT, 경로_길이

시작, 목표 = np.deg2rad([-20.0, 40.0]), np.deg2rad([85.0, 30.0])
반복들, 길이들, 아래로 = [], [], 0
for 씨앗 in range(20):
    경로, _, _, 반복 = RRT(시작, 목표, 선분_충돌, 하한, 상한, np.random.default_rng(씨앗))
    반복들.append(반복)
    길이들.append(경로_길이(경로))
    아래로 += bool((경로[:, 1] < 0).any())          # 팔꿈치를 반대쪽(음수)으로 접어 돌아간 경로
print(f"씨앗 20개: 모두 찾음, 뽑은 횟수 {min(반복들)}~{max(반복들)}번")
print(f"경로 길이 {min(길이들):.2f}~{max(길이들):.2f}rad (평균 {np.mean(길이들):.2f})")
print(f"팔꿈치를 음수 쪽으로 접어 장애물 아래로 돌아간 경로: {아래로}개")
print("같은 씨앗을 다시 쓰면 같은 경로인가?",
      np.array_equal(RRT(시작, 목표, 선분_충돌, 하한, 상한, np.random.default_rng(3))[0],
                     RRT(시작, 목표, 선분_충돌, 하한, 상한, np.random.default_rng(3))[0]))
