import matplotlib.pyplot as plt
import numpy as np

from 동적창 import dwa, 몸_반지름
from 이동도구 import 유니사이클_걸음
from 추종도구 import 가까운_번호, 다시_찍기, 순수_추종

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

경로 = 다시_찍기(np.array([[0.0, 0.0], [7.0, 0.0]]))       # 지도에서 찾은 곧은 길
각 = np.linspace(0, 2 * np.pi, 24, endpoint=False)
둘레 = np.column_stack([np.cos(각), np.sin(각)])


def 장애물들(t: float, 지나는_시각: float) -> list[tuple[np.ndarray, float]]:
    """(중심, 반지름): 길 위에 놓인 상자(지도에 없음)와, x = 5m에서 길을 가로질러 오가는 사람."""
    사람_y = 1.5 * np.sin(0.5 / 1.5 * (t - 지나는_시각))      # 길 한가운데를 0.5m/s로 지난다
    return [(np.array([2.5, 0.1]), 0.3), (np.array([5.0, 사람_y]), 0.2)]


def 달리기(방법: str, 지나는_시각: float):
    포즈, v, ω, 번호 = np.zeros(3), 0.0, 0.0, 0
    궤적, 최소 = [포즈], (np.inf, 0.0)                     # (가장 작은 여유, 그때 로봇 속도)
    for k in range(4000):
        t = k * 0.01
        장애물 = 장애물들(t, 지나는_시각)
        여유 = min(np.linalg.norm(포즈[:2] - c) - r for c, r in 장애물) - 몸_반지름
        최소 = min(최소, (여유, v))
        if np.linalg.norm(포즈[:2] - 경로[-1]) < 0.1:
            break
        if k % 10 == 0:
            번호 = 가까운_번호(경로, 포즈[:2], 번호)
            if 방법 == "순수 추종만":
                v, ω = 순수_추종(포즈, 경로, 번호, 1.0, v=0.4)
            else:
                점들 = np.vstack([c + r * 둘레 for c, r in 장애물])   # 라이다가 본 장애물 둘레
                결과 = dwa(포즈, v, ω, 경로[min(번호 + 20, len(경로) - 1)], 점들)   # 1m 앞 경로 점으로
                v, ω = 결과["v"], 결과["ω"]
        포즈 = 유니사이클_걸음(포즈, v, ω, 0.01)
        궤적.append(포즈)
    return np.array(궤적), t, 최소


# 사람이 길 한가운데를 지나는 시각을 8초부터 18초까지 1초씩 바꿔 11번 달린다
그림, 칸 = plt.subplots(figsize=(8, 3))
for 방법, 색 in [("순수 추종만", "tab:red"), ("DWA", "tab:blue")]:
    결과들 = [달리기(방법, 시각) for 시각 in np.arange(8.0, 18.5, 1.0)]
    부딪힘 = [(여유, v) for _, _, (여유, v) in 결과들 if 여유 < 0]
    print(f"{방법:6s}: 11번 중 부딪힘 {len(부딪힘)}번, 걸린 시간 "
          f"{min(r[1] for r in 결과들):.1f}~{max(r[1] for r in 결과들):.1f}초, "
          f"가장 깊이 겹친 여유 {min(부딪힘)[0]:+.3f}m, 그 순간 로봇 속도 {min(부딪힘)[1]:.2f}m/s")
    궤적 = 결과들[2][0]                                     # 사람이 10초에 지나간 판을 그린다
    칸.plot(궤적[:, 0], 궤적[:, 1], color=색, label=방법)
칸.add_patch(plt.Circle((2.5, 0.1), 0.3, color="0.3"))
칸.plot([5, 5], [-1.5, 1.5], "k:", lw=1, label="사람이 오가는 길")
칸.plot(경로[:, 0], 경로[:, 1], "k--", lw=0.8, label="전역 경로")
칸.set(aspect="equal", xlabel="x(m)")
칸.legend(fontsize=8, ncol=4, loc="lower center", bbox_to_anchor=(0.5, 1.0))
그림.tight_layout()
그림.savefig("dwa_vs_pp.png", dpi=200)
print("저장: dwa_vs_pp.png")
