import matplotlib.pyplot as plt
import numpy as np

from 그림도구 import 방_그리기
from 방장면 import 라이다_스캔, 방_만들기, 스캔_점들
from 포즈도구 import 점_옮기기, 포즈_행렬

모델, 데이터 = 방_만들기()
생성기 = np.random.default_rng(0)
포즈 = np.array([7.6, 6.0, np.deg2rad(150)])     # 오른쪽 위에서 왼쪽 위(150도)를 보는 로봇
점들_로봇 = 스캔_점들(라이다_스캔(모델, 데이터, 포즈, 생성기, 0.02))
T_방_로봇 = 포즈_행렬(포즈)
점들_방 = 점_옮기기(T_방_로봇, 점들_로봇)          # 이름의 안쪽 글자(로봇)가 맞물린다
print("로봇 기준 첫 점:", np.round(점들_로봇[0], 3), "→ 방 기준:", np.round(점들_방[0], 3))

그림, (왼, 오) = plt.subplots(1, 2, figsize=(10, 4.6))
왼.scatter(점들_로봇[:, 0], 점들_로봇[:, 1], s=4, color="tab:red")
왼.arrow(0, 0, 0.6, 0, width=0.06, color="tab:green")      # 로봇의 앞(+x)
왼.set_title("로봇 기준 점구름 (로봇이 원점, 앞이 +x)")
왼.set_aspect("equal")
왼.grid(alpha=0.3)
방_그리기(오, 모델)
오.scatter(점들_방[:, 0], 점들_방[:, 1], s=4, color="tab:red")
오.arrow(포즈[0], 포즈[1], 0.6 * np.cos(포즈[2]), 0.6 * np.sin(포즈[2]), width=0.06, color="tab:green")
오.set_title("방 기준 점구름 (회색: 실제 방)")
for 칸 in (왼, 오):
    칸.set_xlabel("x (m)")
    칸.set_ylabel("y (m)")
그림.tight_layout()
그림.savefig("scan.png", dpi=200)
print("저장: scan.png")
