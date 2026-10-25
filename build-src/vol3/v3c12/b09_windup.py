import matplotlib.pyplot as plt
import numpy as np

from 계단지표 import 계단_지표, 지표_글
from 실전PID import 실전PID
from 진자장면 import 실행

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def 적분항도_적기(제어기: 실전PID, 적분항들: list[float]):
    """제어기를 부를 때마다 적분항을 함께 기록하는 감싸개."""
    def 호출(목표값: float, 측정: float) -> float:
        토크 = 제어기(목표값, 측정)
        적분항들.append(제어기.적분항)
        return 토크
    return 호출


목표, 한계 = np.deg2rad(150), 6.0               # 거의 꼭대기까지, 6N·m짜리 작은 모터로
그림, (위, 아래) = plt.subplots(2, 1, figsize=(7, 5), sharex=True)
for 방식 in ["없음", "클램핑", "역계산"]:
    제어기 = 실전PID(30, 30, 5.7, 주기=0.01, 출력_한계=한계, 와인드업=방식)
    적분항 = []
    기록 = 실행(적분항도_적기(제어기, 적분항), 목표, 시간=5.0, 토크_한계=한계)
    print(f"{방식:4s}: " + 지표_글(계단_지표(기록["시각"], 기록["각도"], 0.0, 목표))
          + f", 가장 높이 {np.rad2deg(기록['각도'].max()):5.1f}도, 적분항 최대 {max(적분항):5.1f}N·m")
    위.plot(기록["시각"], np.rad2deg(기록["각도"]), label=f"와인드업 방지: {방식}")
    아래.plot(기록["시각"], 적분항, label=방식)
위.axhline(150, color="gray", linestyle="--", linewidth=1)
위.axhline(180, color="black", linestyle=":", linewidth=1)
위.set_ylabel("각도(도)")
위.legend(fontsize=8, loc="lower right")
아래.axhline(한계, color="gray", linestyle="--", linewidth=1)
아래.set_ylabel("적분항(N·m)")
아래.set_xlabel("시간(초)")
그림.tight_layout()
그림.savefig("windup.png", dpi=200)
print("저장: windup.png")
