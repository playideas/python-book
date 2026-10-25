import matplotlib.pyplot as plt
import numpy as np

from LQR도구 import LQR
from MPC도구 import 선형MPC
from 이중적분기 import A, B, 주기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

Q = np.diag([1.0, 0.1])
입력_한계 = 1.0                           # 모터가 낼 수 있는 가속도(m/s²)
벽 = 0.05                                # 목표 5cm 뒤에 벽이 있다
x0 = np.array([-2.0, 1.0])               # 2m 앞의 목표로 1m/s로 다가오는 중

K빠른, P빠른 = LQR(A, B, Q, 0.01)
K느린, _ = LQR(A, B, Q, 1.0)
mpc = 선형MPC(A, B, Q, 0.01, P빠른, N=30, 입력_한계=입력_한계, 위치_상한=벽)
제어기들 = {
    "LQR(R=0.01)+자르기": lambda x: np.clip((-K빠른 @ x)[0], -입력_한계, 입력_한계),
    "LQR(R=1)": lambda x: (-K느린 @ x)[0],
    "MPC(N=30)": lambda x: mpc.풀기(x)[0],
}
시각 = np.arange(81) * 주기
그림, 칸들 = plt.subplots(1, 3, figsize=(10, 3.2))
for 이름, 제어기 in 제어기들.items():
    x, 기록, 입력 = x0.copy(), [x0], []
    for _ in range(80):
        u = float(제어기(x))
        x = A @ x + B[:, 0] * u
        기록.append(x)
        입력.append(u)
    기록 = np.array(기록)
    도착 = 시각[np.argmax(np.all(np.abs(기록) < [0.02, 0.05], axis=1))]
    print(f"{이름:17s}: 가장 멀리 {기록[:, 0].max() * 100:5.1f}cm (벽 {벽 * 100:.0f}cm), "
          f"가장 센 입력 {max(np.abs(입력)):.2f}, 멈춘 시각 {도착:.1f}초")
    칸들[0].plot(시각, 기록[:, 0], label=이름)
    칸들[1].plot(시각, 기록[:, 1], label=이름)
    칸들[2].step(시각[:-1], 입력, where="post", label=이름)
칸들[0].axhline(벽, color="black", linewidth=2)
칸들[0].text(0.2, 벽 + 0.08, "벽", fontsize=9)
칸들[0].set_ylim(-2.1, 0.8)
for 칸, 이름 in zip(칸들, ["위치(m)", "속도(m/s)", "입력: 가속도(m/s²)"]):
    칸.set_title(이름, fontsize=10)
    칸.set_xlabel("시간(초)")
칸들[2].axhline(-입력_한계, color="gray", linestyle=":", linewidth=1)
칸들[0].legend(fontsize=8, loc="lower right")
그림.tight_layout()
그림.savefig("mpc_constraints.png", dpi=200)
print("저장: mpc_constraints.png")
