import matplotlib.pyplot as plt
import numpy as np

from 이동도구 import 각도_감싸기, 유니사이클_걸음

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
최고_v, 최고_ω = 0.5, 1.5            # m/s, rad/s


def 점으로_가기(포즈, 목표, 방법: str, k_거리=1.0, k_방향=2.0) -> tuple[float, float]:
    """거리 오차와 방향 오차만 보고 (v, ω)를 정한다. 12장 PID의 P만 쓴 셈이다."""
    dx, dy = 목표 - 포즈[:2]
    거리 = np.hypot(dx, dy)
    방향_오차 = 각도_감싸기(np.arctan2(dy, dx) - 포즈[2])
    v = k_거리 * 거리
    if 방법 == "방향만큼 줄이기":
        v *= max(0.0, np.cos(방향_오차))            # 목표가 옆이나 뒤에 있으면 속도를 줄인다
    elif 방법 == "먼저 돌고 가기":
        v *= abs(방향_오차) < 0.2                   # 약 11도 안으로 들어오기 전에는 서 있는다
    return min(v, 최고_v), float(np.clip(k_방향 * 방향_오차, -최고_ω, 최고_ω))


목표들 = np.array([[2.0, 0.5], [-1.0, 1.0], [0.3, -1.2]])
그림, 칸들 = plt.subplots(1, 3, figsize=(10, 3.6), sharey=True)
for 칸, 방법 in zip(칸들, ["그냥 가기", "방향만큼 줄이기", "먼저 돌고 가기"]):
    결과 = []
    for 목표 in 목표들:
        포즈, 궤적 = np.zeros(3), [np.zeros(3)]
        while np.linalg.norm(목표 - 포즈[:2]) > 0.05 and len(궤적) < 2000:
            포즈 = 유니사이클_걸음(포즈, *점으로_가기(포즈, 목표, 방법), 0.01)
            궤적.append(포즈)
        궤적 = np.array(궤적)
        길이 = np.sum(np.linalg.norm(np.diff(궤적[:, :2], axis=0), axis=1))
        결과.append(f"{len(궤적) * 0.01:.1f}초/{길이:.2f}m")
        칸.plot(궤적[:, 0], 궤적[:, 1])
        칸.plot(*목표, "k*", ms=10)
    print(f"{방법:9s}:", ", ".join(결과))
    칸.set(title=방법, aspect="equal", xlabel="x(m)")
칸들[0].set_ylabel("y(m)")
그림.tight_layout()
그림.savefig("go_to_goal.png", dpi=200)
print("저장: go_to_goal.png")
