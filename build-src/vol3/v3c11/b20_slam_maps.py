import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import distance_transform_edt

from 격자도구 import 지도_만들기, 해상도
from 슬램실습 import 루프_찾기, 정합_오도메트리
from 주행데이터 import 주행_기록
from 포즈그래프 import 그래프_펴기
from 포즈도구 import 포즈_쌓기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

참_포즈들, 바퀴_증분들, 스캔들 = 주행_기록(레이_개수=90)
바퀴_포즈들 = 포즈_쌓기(참_포즈들[0], 바퀴_증분들)
정합_포즈들, 이웃_간선들 = 정합_오도메트리(스캔들, 바퀴_증분들, 참_포즈들[0])
펴진_포즈들 = 그래프_펴기(정합_포즈들, 이웃_간선들 + 루프_찾기(정합_포즈들, 스캔들))


참_찬칸 = 지도_만들기(참_포즈들, 스캔들).확률() > 0.65
그림, 칸들 = plt.subplots(1, 3, figsize=(13, 3.9))
for 칸, 포즈들, 제목 in [(칸들[0], 바퀴_포즈들, "바퀴 오도메트리"),
                     (칸들[1], 정합_포즈들, "스캔 정합 (루프 닫기 전)"),
                     (칸들[2], 펴진_포즈들, "루프 닫기 후")]:
    지도 = 지도_만들기(포즈들, 스캔들)
    확률 = 지도.확률()
    칸.imshow(확률.T, origin="lower", extent=지도.범위(), cmap="gray_r", vmin=0, vmax=1)
    칸.plot(참_포즈들[:, 0], 참_포즈들[:, 1], "-", color="tab:green", lw=1)
    칸.plot(포즈들[:, 0], 포즈들[:, 1], "-", color="tab:red", lw=1)
    칸.set_title(제목)
    칸.set_xticks([])
    칸.set_yticks([])
    # 참 지도의 벽 칸마다, 이 지도의 가장 가까운 벽 칸이 10cm 안에 있는가
    벽까지 = distance_transform_edt(~(확률 > 0.65)) * 해상도
    맞음 = (벽까지[참_찬칸] <= 0.1).mean()
    print(f"{제목:16s}: 참 지도의 벽 칸 중 {맞음:.1%}가 10cm 안에 그려졌다")
그림.tight_layout()
그림.savefig("slam_maps.png", dpi=200)
print("저장: slam_maps.png")
