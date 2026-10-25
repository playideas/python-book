import matplotlib.pyplot as plt
import numpy as np

from 실전PID import 실전PID
from 진자장면 import 실행

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def 목표(t: float) -> float:
    """30도에 있다가 1.5초에 60도로 바꾼다."""
    return np.deg2rad(30 if t < 1.5 else 60)


그림, (위, 아래) = plt.subplots(2, 1, figsize=(7, 4.6), sharex=True)
for 대상, 이름 in [("오차", "오차를 미분"), ("측정", "측정값을 미분")]:
    기록 = 실행(실전PID(30, 30, 5.7, 주기=0.01, 미분_대상=대상), 목표, 시간=2.5)
    바뀐_뒤 = 기록["시각"] >= 1.5
    print(f"{이름}: 목표가 바뀐 순간 요청 토크 {기록['요청'][바뀐_뒤][0]:6.1f}N·m, "
          f"모터가 실제로 낸 가장 큰 토크 {기록['토크'][바뀐_뒤].max():4.1f}N·m")
    위.plot(기록["시각"], np.rad2deg(기록["각도"]), label=이름)
    아래.plot(기록["시각"], 기록["요청"], label=이름)
위.plot(기록["시각"], np.rad2deg(기록["목표"]), color="gray", linestyle="--", linewidth=1, label="목표")
위.set_ylim(25, 68)
위.set_ylabel("각도(도)")
위.legend(fontsize=8, loc="lower right")
아래.set_ylabel("요청 토크(N·m)")
아래.set_xlabel("시간(초)")
아래.set_xlim(1.3, 2.5)
그림.tight_layout()
그림.savefig("derivative_kick.png", dpi=200)
print("저장: derivative_kick.png")
