import matplotlib.pyplot as plt

from 격자도구 import 지도_만들기
from 주행데이터 import 주행_기록
from 포즈도구 import 포즈_쌓기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

참_포즈들, 바퀴_증분들, 스캔들 = 주행_기록()
바퀴_포즈들 = 포즈_쌓기(참_포즈들[0], 바퀴_증분들)

그림, 칸들 = plt.subplots(1, 3, figsize=(13, 3.9))
for 칸, 포즈들, 개수, 제목 in [(칸들[0], 참_포즈들, 1, "스캔 1개"),
                          (칸들[1], 참_포즈들, 85, "참 포즈로 85개 (매핑)"),
                          (칸들[2], 바퀴_포즈들, 85, "바퀴 오도메트리로 85개")]:
    지도 = 지도_만들기(포즈들[:개수], 스캔들[:개수])
    확률 = 지도.확률()
    칸.imshow(확률.T, origin="lower", extent=지도.범위(), cmap="gray_r", vmin=0, vmax=1)
    칸.set_title(제목)
    칸.set_xticks([])
    칸.set_yticks([])
    print(f"{제목:14s}: 찬칸 쪽 {(확률 > 0.5).sum():5d}, 빈칸 쪽 {(확률 < 0.5).sum():5d}, "
          f"모름 {(확률 == 0.5).sum():5d} (전체 {확률.size}칸)")
그림.tight_layout()
그림.savefig("grid_maps.png", dpi=200)
print("저장: grid_maps.png")
