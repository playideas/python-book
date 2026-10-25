import matplotlib.pyplot as plt
import numpy as np

from 그림도구 import 방_그리기
from 방장면 import 방_만들기
from 주행데이터 import 주행_기록
from 포즈도구 import 각도_정리, 점_옮기기, 포즈_쌓기, 포즈_행렬

참_포즈들, 바퀴_증분들, 스캔들 = 주행_기록()
print("포즈 수:", len(참_포즈들), "/ 첫 바퀴 증분(앞, 왼쪽, 회전):", np.round(바퀴_증분들[0], 4))
바퀴_포즈들 = 포즈_쌓기(참_포즈들[0], 바퀴_증분들)     # 잰 증분을 차례로 이어 붙인다(추측 항법)

위치_오차 = np.linalg.norm(바퀴_포즈들[:, :2] - 참_포즈들[:, :2], axis=1)
방향_오차 = np.rad2deg(np.abs(각도_정리(바퀴_포즈들[:, 2] - 참_포즈들[:, 2])))
for k in [21, 42, 63, 84]:
    print(f"{k:2d}걸음 뒤: 위치 오차 {위치_오차[k]:.3f}m, 방향 오차 {방향_오차[k]:.1f}도")

모델 = 방_만들기()[0]
그림, 칸들 = plt.subplots(1, 2, figsize=(10, 4.4))
for 칸, 포즈들, 제목 in [(칸들[0], 참_포즈들, "참 포즈로 쌓은 점 지도"),
                     (칸들[1], 바퀴_포즈들, "바퀴 오도메트리로 쌓은 점 지도")]:
    방_그리기(칸, 모델, 색="0.88")
    # 스캔마다 '그때의 포즈'로 방 기준에 옮겨 한 장에 겹친다
    점_지도 = np.vstack([점_옮기기(포즈_행렬(포즈), 스캔) for 포즈, 스캔 in zip(포즈들, 스캔들)])
    칸.scatter(점_지도[:, 0], 점_지도[:, 1], s=0.3, color="tab:red")
    칸.plot(포즈들[:, 0], 포즈들[:, 1], "-", color="tab:blue", lw=1)
    칸.set_title(제목)
    칸.set_xlim(-1.5, 11)
    칸.set_ylim(-1.5, 9.5)
그림.tight_layout()
그림.savefig("odom_map.png", dpi=200)
print("저장: odom_map.png")
