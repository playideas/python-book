import matplotlib.pyplot as plt
import numpy as np

from 경로도구 import 제어_주기, 관절_경로, 직선_경로
from 잡기도구 import TCP_포즈, 역기구학, 집기_포즈
from 팔집게장면 import 집_자세

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

출발, 도착 = np.array([0.45, 0.2, 0.55]), np.array([0.3, -0.25, 0.5])   # 상자 위 → 놓을 곳 위
q_출발 = 역기구학(집기_포즈(출발, 180), 집_자세)
q_도착 = 역기구학(집기_포즈(도착, 90), q_출발)

그림, (위에서, 옆에서) = plt.subplots(1, 2, figsize=(9, 3.6))
print("[옮기기] 상자 위 → 놓을 곳 위, 2초")
for 이름, 경로, 색 in [("관절 공간", 관절_경로(q_출발, q_도착, 2.0), "tab:orange"),
                      ("작업 공간 직선", 직선_경로(q_출발, 집기_포즈(도착, 90), 2.0), "tab:blue")]:
    점들 = np.array([TCP_포즈(q)[:3, 3] for q in [q_출발, *경로]])
    방향 = (도착 - 출발) / np.linalg.norm(도착 - 출발)
    벗어남 = np.linalg.norm((점들 - 출발) - np.outer((점들 - 출발) @ 방향, 방향), axis=1)
    관절_속도 = np.abs(np.diff(np.array([q_출발, *경로]), axis=0)).max(axis=0) / 제어_주기
    길이 = np.linalg.norm(np.diff(점들, axis=0), axis=1).sum()
    print(f"{이름:8s}: TCP 길이 {길이:.3f}m (직선 {np.linalg.norm(도착 - 출발):.3f}m), 직선에서 최대 {벗어남.max() * 100:.1f}cm, "
          f"가장 빠른 관절 {np.rad2deg(관절_속도.max()):.0f}도/초")
    위에서.plot(점들[:, 1], 점들[:, 0], color=색, label=이름)

print("[내려가기] (0.3, 0) 위 20cm → 집는 높이, 1초")
위, 아래 = np.array([0.3, 0.0, 0.625]), np.array([0.3, 0.0, 0.425])
q_위 = 역기구학(집기_포즈(위, 180), 집_자세)
q_아래 = 역기구학(집기_포즈(아래, 180), q_위)
for 이름, 경로, 색 in [("관절 공간", 관절_경로(q_위, q_아래, 1.0), "tab:orange"),
                      ("작업 공간 직선", 직선_경로(q_위, 집기_포즈(아래, 180), 1.0), "tab:blue")]:
    점들 = np.array([TCP_포즈(q)[:3, 3] for q in [q_위, *경로]])
    옆으로_mm = np.linalg.norm(점들[:, :2] - 위[:2], axis=1) * 1000
    print(f"{이름:8s}: 옆으로 최대 {옆으로_mm.max():.1f}mm 벗어남")
    옆에서.plot(np.arange(len(점들)) * 제어_주기, 옆으로_mm, color=색, label=이름)
위에서.plot([출발[1], 도착[1]], [출발[0], 도착[0]], "ko", markersize=4)
위에서.set_xlabel("y (m, 왼쪽이 +)")
위에서.set_ylabel("x (m, 앞)")
위에서.invert_xaxis()
위에서.set_aspect("equal")
위에서.set_title("위에서 본 TCP 길", fontsize=10)
옆에서.set_xlabel("시간(초)")
옆에서.set_ylabel("옆으로 벗어난 거리(mm)")
옆에서.set_title("20cm 곧게 내려가기", fontsize=10)
옆에서.legend(fontsize=8)
그림.tight_layout()
그림.savefig("paths.png", dpi=200)
print("저장: paths.png")
