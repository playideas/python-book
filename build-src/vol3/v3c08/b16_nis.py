import numpy as np

from 등속데이터 import 등속_모델, 참_위치, 측정
from 칼만도구 import 갱신, 예측

H = np.array([[1.0, 0.0]])
print(" 설정                | 혁신 평균 | NIS 평균 | ±2√S 밖 | 실제 위치 RMS | 필터가 말하는 σ")
for 이름, q, R값 in [("맞게(q 0.1, R 0.1²)", 0.1, 0.1**2), ("R을 너무 작게", 0.1, 0.02**2),
                    ("R을 너무 크게", 0.1, 0.5**2), ("q를 너무 작게", 1e-4, 0.1**2)]:
    F, Q = 등속_모델(q)
    R = np.array([[R값]])
    x, P = np.array([측정[0], 0.0]), np.diag([0.1**2, 1.0])
    혁신들, nis들, 추정 = [], [], []
    for z in 측정:
        x, P = 예측(x, P, F, Q)
        x, P, 혁신, S = 갱신(x, P, np.array([z]), H, R)
        혁신들.append(혁신[0])
        nis들.append(float(혁신 @ np.linalg.inv(S) @ 혁신))    # 혁신을 S로 잰 크기
        추정.append(x[0])
    혁신들, nis들 = np.array(혁신들[10:]), np.array(nis들[10:])
    밖 = np.mean(nis들 > 4)                                      # |혁신| > 2√S 와 같다
    rms = np.sqrt(np.mean((np.array(추정[10:]) - 참_위치[10:]) ** 2))
    print(f" {이름:18s} | {혁신들.mean():+.3f}m | {nis들.mean():7.2f} | {밖:6.1%} | {rms:.3f}m | {np.sqrt(P[0, 0]):.3f}m")
