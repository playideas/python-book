import numpy as np

from 정합도구 import 최적_변환
from 포즈도구 import 점_옮기기, 포즈_행렬, 행렬_포즈

생성기 = np.random.default_rng(0)
기준 = 생성기.uniform(-3, 3, size=(50, 2))              # 아무렇게나 흩어진 점 50개
T_기준_원본 = 포즈_행렬([0.4, -0.2, np.deg2rad(25)])     # 참 변환: 0.4m, -0.2m, 25도
원본 = 점_옮기기(np.linalg.inv(T_기준_원본), 기준)       # 같은 점을 원본 기준으로 다시 적은 것
원본 = 원본 + 생성기.normal(0, 0.02, 원본.shape)          # 잴 때 생긴 잡음

# 짝(같은 번호끼리 같은 점)을 알 때는 한 번에 답이 나온다
T = 최적_변환(원본, 기준)
x, y, 각 = 행렬_포즈(T)
print(f"찾은 변환: x {x:.3f}m, y {y:.3f}m, 각 {np.rad2deg(각):.2f}도")
print("겹친 뒤 평균 거리:", round(float(np.linalg.norm(점_옮기기(T, 원본) - 기준, axis=1).mean()), 4), "m")

# 짝을 섞어 버리면? 같은 계산이 엉뚱한 답을 낸다
섞인_번호 = 생성기.permutation(50)
x, y, 각 = 행렬_포즈(최적_변환(원본, 기준[섞인_번호]))
print(f"짝이 틀리면  : x {x:.3f}m, y {y:.3f}m, 각 {np.rad2deg(각):.2f}도")
