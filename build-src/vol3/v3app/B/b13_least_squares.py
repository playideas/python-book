import numpy as np
from scipy.optimize import least_squares

# 모르는 값이 식 안에 비선형으로 들어 있을 때: 감쇠 진동 기록에서 감쇠율과 진동수 찾기(20장 시스템 식별의 맛)
rng = np.random.default_rng(0)
t = np.linspace(0, 3, 150)


def 모델(값: np.ndarray, t: np.ndarray) -> np.ndarray:
    감쇠율, 진동수 = 값
    return np.exp(-감쇠율 * t) * np.cos(2 * np.pi * 진동수 * t)


기록 = 모델(np.array([0.8, 1.5]), t) + rng.normal(0, 0.02, t.size)
결과 = least_squares(lambda 값: 모델(값, t) - 기록, x0=[0.5, 1.4], bounds=([0, 0.1], [5, 5]))
print("찾은 감쇠율, 진동수:", np.round(결과.x, 3), " 차이 제곱합의 절반:", round(결과.cost, 4))

처음_차이 = 모델(np.array([0.5, 1.4]), t) - 기록
print(f"처음값 [0.5, 1.4]의 차이 제곱합의 절반: {0.5 * np.sum(처음_차이**2):.4f}, 함수 계산 {결과.nfev}번")
