import matplotlib.pyplot as plt
import numpy as np

from 시간매기기 import 스플라인, 안전한_스플라인
from 팔공간 import 관절공간_지도, 상한, 선분_충돌, 여유, 하한
from 표본계획 import RRT, 경로_길이, 지름길

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

시작, 목표 = np.deg2rad([-20.0, 40.0]), np.deg2rad([85.0, 30.0])
날것, _, _, _ = RRT(시작, 목표, 선분_충돌, 하한, 상한, np.random.default_rng(0))
짧게 = 지름길(날것, 선분_충돌, np.random.default_rng(1))
곡선 = 스플라인(짧게)
안전_곡선, 횟수 = 안전한_스플라인(짧게, lambda 점들: bool((여유(점들) < 0).any()))
print(f"RRT 그대로: 꼭짓점 {len(날것)}개, 길이 {경로_길이(날것):.3f}rad")
print(f"지름길 뒤: 꼭짓점 {len(짧게)}개, 길이 {경로_길이(짧게):.3f}rad")
for 이름, 경로 in [("스플라인", 곡선), ("안전 스플라인", 안전_곡선)]:
    print(f"{이름}: 길이 {경로_길이(경로):.3f}rad, 가장 좁은 여유 {여유(경로).min() * 1000:.1f}mm")
print(f"가운데 점 넣기 {횟수}번 만에 안전: 경유점 {len(짧게)}개 → {(len(짧게) - 1) * 2**횟수 + 1}개")

그림, 칸 = plt.subplots(figsize=(5.6, 4.6))
칸.imshow(관절공간_지도().T, origin="lower", extent=[-180, 180, -180, 180], cmap="gray_r", vmin=0, vmax=1.6)
칸.plot(*np.rad2deg(날것).T, color="tab:cyan", linewidth=1, label="RRT 그대로")
칸.plot(*np.rad2deg(짧게).T, "o--", color="tab:orange", markersize=4, label="지름길 뒤")
칸.plot(*np.rad2deg(곡선).T, ":", color="tab:purple", linewidth=2, label="스플라인(파고듦)")
칸.plot(*np.rad2deg(안전_곡선).T, color="tab:red", linewidth=2, label="안전 스플라인")
칸.set(xlim=(-60, 120), ylim=(-20, 180), xlabel="어깨 (도)", ylabel="팔꿈치 (도)")
칸.legend(fontsize=8, loc="lower right")
그림.tight_layout()
그림.savefig("smooth.png", dpi=200)
print("저장: smooth.png")
