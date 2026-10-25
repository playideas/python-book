import matplotlib.pyplot as plt
import numpy as np

from 바퀴로봇 import 각도_감싸기, ekf_갱신, ekf_예측, 표지_R, 표지_보기
from 시험길 import 시험_경로
from 추종도구 import 따라_달리기, 순수_추종, 옆_오차들

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
표지들 = np.array([[1.5, 3.0], [4.5, 3.5], [3.5, -1.0], [8.0, 1.0]])


def 위치_추정기(출처: str, 생성기: np.random.Generator):
    """0.1초마다 참 포즈를 받아, 제어기에 줄 포즈(참, 오도메트리, EKF)를 돌려주는 함수를 만든다."""
    기록 = {"추정": np.zeros(3), "P": np.eye(3) * 1e-4, "이전_참": np.zeros(3), "참들": [], "추정들": [], "점프": [0.0]}

    def 알기(참: np.ndarray) -> np.ndarray:
        # 오도메트리: 실제 움직임에 잡음과, 늘 왼쪽으로 더 돌았다고 세는 치우침(0.001rad)이 섞인다
        이동 = np.linalg.norm(참[:2] - 기록["이전_참"][:2]) * (1 + 생성기.normal(0, 0.03))
        회전 = 각도_감싸기(참[2] - 기록["이전_참"][2]) + 0.001 + 생성기.normal(0, 0.002)
        기록["이전_참"] = 참.copy()
        추정, P = ekf_예측(기록["추정"], 기록["P"], 이동, 회전)
        if 출처 == "EKF" and len(기록["참들"]) % 5 == 0:          # 0.5초마다 표지 측정
            고치기_전 = 추정[:2].copy()
            for 표지 in 표지들:
                z = 표지_보기(참, 표지) + 생성기.normal(0, np.sqrt(np.diag(표지_R)))
                if z[0] < 4.0 and abs(z[1]) < np.deg2rad(60):
                    추정, P, _, _ = ekf_갱신(추정, P, z, 표지, 표지_R)
            기록["점프"].append(np.linalg.norm(추정[:2] - 고치기_전))   # 측정 한 번에 추정이 뛴 거리
        기록["추정"], 기록["P"] = 추정, P
        기록["참들"].append(참)
        기록["추정들"].append(추정)
        return 참 if 출처 == "참 포즈" else 추정
    return 알기, 기록


그림, 칸 = plt.subplots(figsize=(9, 4.4))
칸.plot(시험_경로[:, 0], 시험_경로[:, 1], "k--", lw=1, label="경로")
for 출처, 색 in [("참 포즈", "tab:green"), ("오도메트리만", "tab:red"), ("EKF", "tab:blue")]:
    알기, 기록 = 위치_추정기(출처, np.random.default_rng(0))
    제어기 = lambda 포즈, 경로, 번호: 순수_추종(포즈, 경로, 번호, 0.4, v=0.4)
    궤적 = 따라_달리기(시험_경로, 제어기, [0, 0, 0], 위치_알기=알기)
    오차 = 옆_오차들(시험_경로, 궤적)
    추정_오차 = np.linalg.norm(np.array(기록["참들"])[:, :2] - np.array(기록["추정들"])[:, :2], axis=1)
    print(f"{출처:6s}: 실제 옆 오차 평균 {오차.mean():.3f}m, 최대 {오차.max():.3f}m, "
          f"끝점에서 {np.linalg.norm(궤적[-1, :2] - 시험_경로[-1]):.3f}m 빗나감")
    if 출처 != "참 포즈":
        print(f"        추정 오차 평균 {추정_오차.mean():.3f}m, 끝에서 {추정_오차[-1]:.3f}m"
              + (f", 측정 한 번에 추정이 뛴 거리 최대 {max(기록['점프']):.3f}m" if 출처 == "EKF" else ""))
    칸.plot(궤적[:, 0], 궤적[:, 1], color=색, lw=1.3, label=f"{출처}로 달린 실제 궤적")
칸.plot(*표지들.T, "^", color="tab:purple", ms=9, label="표지")
칸.set(aspect="equal", xlabel="x(m)", ylabel="y(m)")
칸.legend(fontsize=8, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.2))
그림.tight_layout()
그림.savefig("follow_estimate.png", dpi=200)
print("저장: follow_estimate.png")
