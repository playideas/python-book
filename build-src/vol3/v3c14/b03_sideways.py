import matplotlib.pyplot as plt
import numpy as np

from 이동도구 import 유니사이클_걸음

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def 달리기(포즈, 명령들, dt=0.05):
    """(v, ω, 초) 명령을 차례로 따라 달린 포즈들."""
    포즈들 = [np.array(포즈, dtype=float)]
    for v, ω, 초 in 명령들:
        for _ in range(round(초 / dt)):
            포즈들.append(유니사이클_걸음(포즈들[-1], v, ω, dt))
    return np.array(포즈들)


그림, 칸 = plt.subplots(figsize=(6, 4.6))
# 바로 왼쪽 0.5m로 옮겨 가기: 옆걸음이 안 되니 돌고, 가고, 다시 돈다
사분_ω = np.pi / 4                    # 2초에 90도 도는 각속도
방법들 = {"돌고·가고·돌기": [(0, 사분_ω, 2), (0.25, 0, 2), (0, -사분_ω, 2)],
        "평행 주차(뒤로 S자, 앞으로)": [(-0.25 * 사분_ω, -사분_ω, 2), (-0.25 * 사분_ω, 사분_ω, 2), (0.25, 0, 2)]}
for 이름, 명령들 in 방법들.items():
    궤적 = 달리기([0, 0, 0], 명령들)
    칸.plot(궤적[:, 0], 궤적[:, 1], label=f"{이름} ({sum(초 for *_, 초 in 명령들)}초)")
    x, y, θ = np.round(궤적[-1], 3) + 0.0                       # + 0.0: -0.0을 0.0으로
    print(f"{이름}: 끝 포즈 x {x:.3f}, y {y:.3f}, θ {np.rad2deg(θ):.1f}도")
칸.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.2))
칸.set(aspect="equal", xlabel="x(m)", ylabel="y(m)")
그림.tight_layout()
그림.savefig("sideways.png", dpi=200)
print("저장: sideways.png")
