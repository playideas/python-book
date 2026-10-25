import matplotlib.pyplot as plt
import numpy as np

from 시험길 import 시험_경로
from 추종도구 import 순수_추종, 스탠리, 옆_오차들, 따라_달리기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

그림, 칸 = plt.subplots(figsize=(9, 3.4))
칸.plot(시험_경로[:, 0], 시험_경로[:, 1], "k--", lw=1, label="경로")
for 앞_거리 in [0.15, 0.3, 0.6, 1.2]:
    제어기 = lambda 포즈, 경로, 번호: 순수_추종(포즈, 경로, 번호, 앞_거리, v=0.4)
    궤적 = 따라_달리기(시험_경로, 제어기, [0, 0, 0])
    오차 = 옆_오차들(시험_경로, 궤적)
    print(f"앞을 보는 거리 {앞_거리:.2f}m: 걸린 시간 {len(궤적) * 0.01:.1f}초, "
          f"옆 오차 평균 {오차.mean():.3f}m, 최대 {오차.max():.3f}m")
    칸.plot(궤적[:, 0], 궤적[:, 1], lw=1.3, label=f"{앞_거리}m")
# 비교: 앞을 보지 않고 가장 가까운 점의 방향·옆 오차를 보는 스탠리
궤적 = 따라_달리기(시험_경로, lambda 포즈, 경로, 번호: 스탠리(포즈, 경로, 번호, v=0.4, k=2.0), [0, 0, 0])
오차 = 옆_오차들(시험_경로, 궤적)
print(f"스탠리(k=2)        : 걸린 시간 {len(궤적) * 0.01:.1f}초, 옆 오차 평균 {오차.mean():.3f}m, 최대 {오차.max():.3f}m")
칸.set_aspect("equal")
칸.legend(fontsize=8, ncol=5, loc="lower right")
칸.set(xlabel="x(m)", ylabel="y(m)")
그림.tight_layout()
그림.savefig("pure_pursuit.png", dpi=200)
print("저장: pure_pursuit.png")
