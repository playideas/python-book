import matplotlib.pyplot as plt
import numpy as np

from 그림도구 import 방_그리기
from 방장면 import 방_만들기
from 정합도구 import icp
from 주행데이터 import 주행_기록
from 포즈도구 import 포즈_잇기, 포즈_행렬, 행렬_포즈

참_포즈들, 바퀴_증분들, 스캔들 = 주행_기록()
바퀴_포즈들 = [참_포즈들[0]]
정합_포즈들 = [참_포즈들[0]]
for k, 증분 in enumerate(바퀴_증분들):
    바퀴_포즈들.append(포즈_잇기(바퀴_포즈들[-1], 증분))
    # 바퀴가 잰 증분을 처음 추측으로 주고, 스캔끼리 맞춰 고친다
    T_이전_지금, _ = icp(스캔들[k + 1], 스캔들[k], 포즈_행렬(증분))
    정합_포즈들.append(포즈_잇기(정합_포즈들[-1], 행렬_포즈(T_이전_지금)))
바퀴_포즈들, 정합_포즈들 = np.array(바퀴_포즈들), np.array(정합_포즈들)

for 이름, 포즈들 in [("바퀴 오도메트리", 바퀴_포즈들), ("스캔 정합 오도메트리", 정합_포즈들)]:
    오차 = np.linalg.norm(포즈들[:, :2] - 참_포즈들[:, :2], axis=1)
    print(f"{이름:12s}: 끝 위치 오차 {오차[-1]:.3f}m, 가장 클 때 {오차.max():.3f}m ({오차.argmax()}걸음)")

그림, 칸 = plt.subplots(figsize=(6, 4.8))
방_그리기(칸, 방_만들기()[0])
칸.plot(참_포즈들[:, 0], 참_포즈들[:, 1], "k-", label="참 궤적")
칸.plot(바퀴_포즈들[:, 0], 바퀴_포즈들[:, 1], "--", color="tab:orange", label="바퀴 오도메트리")
칸.plot(정합_포즈들[:, 0], 정합_포즈들[:, 1], "-", color="tab:blue", label="스캔 정합 오도메트리")
칸.set_xlabel("x (m)")
칸.set_ylabel("y (m)")
칸.legend(loc="upper right", fontsize=9)
그림.tight_layout()
그림.savefig("icp_traj.png", dpi=200)
print("저장: icp_traj.png")
