import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def 정규분포(x: np.ndarray, 평균: float, 표준편차: float) -> np.ndarray:
    return np.exp(-0.5 * ((x - 평균) / 표준편차) ** 2) / (표준편차 * np.sqrt(2 * np.pi))


평균1, 표준편차1 = 10.0, 4.0      # 자이로를 쌓아 짐작한 피치(도)
평균2, 표준편차2 = 16.0, 3.0      # 가속도계로 읽은 피치(도)

# 공식: 분산이 작은(더 믿을 만한) 쪽에 더 끌려간다
분산 = 1 / (1 / 표준편차1**2 + 1 / 표준편차2**2)
평균 = 분산 * (평균1 / 표준편차1**2 + 평균2 / 표준편차2**2)
print(f"공식: 평균 {평균:.2f}도, 표준편차 {np.sqrt(분산):.2f}도")

# 검산: 두 곡선을 칸마다 곱하고 넓이를 1로 맞춘 뒤 평균과 표준편차를 잰다
x = np.linspace(-10, 40, 50001)
곱 = 정규분포(x, 평균1, 표준편차1) * 정규분포(x, 평균2, 표준편차2)
곱 /= np.trapezoid(곱, x)
수치_평균 = np.trapezoid(x * 곱, x)
수치_표준편차 = np.sqrt(np.trapezoid((x - 수치_평균) ** 2 * 곱, x))
print(f"수치: 평균 {수치_평균:.2f}도, 표준편차 {수치_표준편차:.2f}도")

그림, 칸 = plt.subplots(figsize=(7, 3))
칸.plot(x, 정규분포(x, 평균1, 표준편차1), label=f"자이로 짐작 {평균1:.0f}±{표준편차1:.0f}도")
칸.plot(x, 정규분포(x, 평균2, 표준편차2), label=f"가속도계 {평균2:.0f}±{표준편차2:.0f}도")
칸.plot(x, 곱, color="black", lw=2, label=f"둘을 곱한 것 {평균:.1f}±{np.sqrt(분산):.1f}도")
칸.set_xlim(-5, 30)
칸.set_xlabel("피치(도)")
칸.set_ylabel("밀도")
칸.legend(fontsize=8)
그림.tight_layout()
그림.savefig("gauss_product.png", dpi=200)
print("저장: gauss_product.png")
