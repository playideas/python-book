import matplotlib.pyplot as plt
import numpy as np

from 격자도구 import 지도_만들기
from 입자도구 import 다시_뽑기, 벽까지_거리표, 입자_가중치, 입자_뿌리기, 입자_움직이기
from 주행데이터 import 주행_기록

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

참_포즈들, 바퀴_증분들, 스캔들 = 주행_기록()
지도 = 지도_만들기(참_포즈들, 스캔들)       # 11.4절처럼 참 포즈로 만든 지도를 '알고 있다'
확률 = 지도.확률()
거리표 = 벽까지_거리표(확률)

생성기 = np.random.default_rng(1)
입자들 = 입자_뿌리기(2000, 확률, 생성기)             # 어디 있는지 전혀 모른다
찍을_걸음 = [0, 1, 3, 12]
그림, 칸들 = plt.subplots(1, 4, figsize=(13, 3.3))
칸_번호 = 0
for k in range(25):
    if k > 0:
        입자들 = 입자_움직이기(입자들, 바퀴_증분들[k - 1], 생성기)   # 예측: 바퀴가 잰 만큼 다 같이 움직인다
    가중치 = 입자_가중치(입자들, 스캔들[k][::12], 거리표)          # 갱신: 스캔 15점이 벽에 붙는 만큼 점수
    추정 = np.average(입자들[:, :2], weights=가중치, axis=0)
    퍼짐 = np.sqrt(np.average(((입자들[:, :2] - 추정) ** 2).sum(axis=1), weights=가중치))
    if k in 찍을_걸음 or k == 24:
        오차 = np.linalg.norm(추정 - 참_포즈들[k, :2])
        print(f"{k:2d}걸음: 추정 오차 {오차:.3f}m, 입자 퍼짐 {퍼짐:.3f}m, 유효 입자 수 {1 / np.sum(가중치 ** 2):6.1f}")
    if k in 찍을_걸음:
        칸 = 칸들[칸_번호]
        칸.imshow(확률.T, origin="lower", extent=지도.범위(), cmap="gray_r", vmin=0, vmax=1)
        칸.scatter(입자들[:, 0], 입자들[:, 1], s=1, color="tab:orange")
        칸.plot(*참_포즈들[k, :2], "*", color="tab:blue", ms=12)
        칸.set_title(f"{k}걸음 (입자 2000개)" if k == 0 else f"{k}걸음")
        칸.set_xticks([])
        칸.set_yticks([])
        칸_번호 += 1
    입자들 = 다시_뽑기(입자들, 가중치, 생성기)          # 점수 높은 입자는 늘고 낮은 입자는 사라진다
그림.tight_layout()
그림.savefig("mcl.png", dpi=200)
print("저장: mcl.png")
