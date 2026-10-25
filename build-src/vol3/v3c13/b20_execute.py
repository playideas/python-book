import matplotlib.pyplot as plt
import numpy as np

from 실습계획 import 계획하기
from 실습장면 import 기둥들, 목표_자세
from 실행도구 import 실행

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

정보, 총시간, 자세 = 계획하기(씨앗=0)
print("계획:", ", ".join(f"{k} {v}" for k, v in 정보.items()), f"/ 걸리는 시간 {총시간:.3f}초")

한번에 = 실행(lambda t: 목표_자세, 시간=3.0)            # 4장처럼 목표 자세를 처음부터 한 번에 준다
계획대로 = 실행(자세, 시간=총시간 + 0.5)                 # 계획한 궤적을 따라가고 0.5초 더 지켜본다
그림, (왼쪽, 오른쪽) = plt.subplots(1, 2, figsize=(10, 4.2), gridspec_kw={"width_ratios": [1, 1.3]})
for 기록, 이름, 색 in [(한번에, "한 번에 목표", "tab:red"), (계획대로, "계획한 궤적", "tab:blue")]:
    닿음 = 기록["접촉"] > 0
    print(f"[{이름}] 기둥과 닿은 시간 {닿음.sum() * 0.002:.3f}초, 가장 좁은 거리 {기록['거리'].min() * 1000:.1f}mm, "
          f"가장 빠른 관절 {np.abs(np.diff(기록['관절'], axis=0)).max() / 0.002:.2f}rad/s, "
          f"마지막 관절 {np.rad2deg(기록['관절'][-1]).round(1)}도")
    왼쪽.plot(*기록["손끝"].T, color=색, label=이름)
    오른쪽.plot(기록["시각"], 기록["거리"] * 1000, color=색, label=이름)
print(f"[계획한 궤적] 목표와 실제 관절의 차이: 가장 클 때 "
      f"{np.rad2deg(np.abs(계획대로['관절'] - 계획대로['목표']).max(axis=0)).round(2)}도")

for x, y, r in 기둥들:
    왼쪽.add_patch(plt.Circle((x, y), r, color="sienna"))
왼쪽.plot(0, 0, "ks")
왼쪽.set(xlim=(-0.45, 0.75), ylim=(-0.65, 0.6), aspect="equal", xlabel="x (m)", ylabel="y (m)",
        title="위에서 본 손끝 경로")
왼쪽.legend(fontsize=8, loc="lower left")
오른쪽.axhline(0, color="k", linewidth=0.8)
오른쪽.axhline(30, color="gray", linestyle=":", label="계획 여유 30mm")
오른쪽.set(xlabel="시간 (초)", ylabel="팔과 기둥 사이 거리 (mm)", title="음수 = 기둥을 파고듦")
오른쪽.legend(fontsize=8)
그림.tight_layout()
그림.savefig("arm_compare.png", dpi=200)
print("저장: arm_compare.png")
