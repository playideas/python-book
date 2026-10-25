import matplotlib.pyplot as plt

from 격자도구 import 해상도
from 지도준비 import 로봇_반지름, 막힌_칸, 부풀리기, 칸

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

막힘 = 막힌_칸()                                # 11장 지도: 찬칸·모르는 칸 = 막힘
통과 = 부풀리기(막힘, 로봇_반지름)               # 로봇 반지름만큼 벽을 두껍게
print(f"칸 한 변 {해상도}m, 전체 {막힘.size}칸")
print(f"빈칸 {(~막힘).sum()}칸 → 부풀린 뒤 로봇 중심을 둘 수 있는 칸 {통과.sum()}칸")
for 이름, 점 in [("기둥과 아래 벽 사이 틈 (5.0, 0.2)", (5.0, 0.2)),
                ("섬 아래 넓은 통로 (5.0, 2.0)", (5.0, 2.0))]:
    원래 = "빈칸" if not 막힘[칸(점)] else "막힘"
    부풀림 = "통과" if 통과[칸(점)] else "막힘"
    print(f"{이름}: 원래 지도 {원래}, 부풀린 지도 {부풀림}")

그림, 칸들 = plt.subplots(1, 2, figsize=(10, 4.5))
범위 = [-0.5, 10.5, -0.5, 8.5]
for 그림칸, 배열, 제목 in [(칸들[0], 막힘, "11장 지도 (로봇 = 원)"), (칸들[1], ~통과, "부풀린 지도 (로봇 = 점)")]:
    그림칸.imshow(배열.T, origin="lower", extent=범위, cmap="gray_r", vmin=0, vmax=1.6)
    그림칸.set(title=제목, xlabel="x (m)", ylabel="y (m)")
for 점, 색 in [((5.0, 0.2), "tab:red"), ((5.0, 2.0), "tab:blue")]:
    칸들[0].add_patch(plt.Circle(점, 로봇_반지름, fill=False, color=색, linewidth=1.5))
    칸들[1].plot(*점, "o", color=색, markersize=4)
그림.tight_layout()
그림.savefig("inflate.png", dpi=200)
print("저장: inflate.png")
