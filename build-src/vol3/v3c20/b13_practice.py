from dataclasses import replace

import matplotlib.pyplot as plt
import numpy as np

from 무작위화 import 가장_좋은_칸, 무작위_물성, 점수표
from 식별 import 식별
from 팔제어 import 목표, 성적, 제어기_만들기
from 현실팔 import 물성, 시뮬_물성, 실행, 현실_물성

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def 들뜸(t: float, q: np.ndarray) -> np.ndarray:
    return np.array([3.0 * np.sin(2 * np.pi * 0.7 * t) + 2.0 * np.sin(2 * np.pi * 1.9 * t),
                     1.2 * np.sin(2 * np.pi * 1.1 * t) + 0.8 * np.sin(2 * np.pi * 2.7 * t)])


# 1) 현실 역할 팔에서 6초 기록 → 시스템 식별. 남은 차이를 측정 잡음의 크기로 삼는다
찾은, rms = 식별(들뜸, 실행(들뜸, 6.0, 현실_물성, 시드=1), 보이기=False)
식별_모델 = replace(찾은, 잡음=np.deg2rad(rms))


def 식별_둘레(생성기: np.random.Generator) -> 물성:
    """식별한 값 둘레를 좁게 흔들고, 앞으로 집을 짐(0~0.4kg)과 모르는 유격까지 더한다."""
    p = 식별_모델
    return replace(p, 끝_질량=p.끝_질량 * 생성기.uniform(0.9, 1.1) + 생성기.uniform(0, 0.4),
                   감쇠=p.감쇠 * 생성기.uniform(0.8, 1.2), 마찰=p.마찰 * 생성기.uniform(0.8, 1.2),
                   토크_배율=p.토크_배율 * 생성기.uniform(0.95, 1.05),
                   지연=p.지연 + int(생성기.integers(0, 2)), 유격=np.deg2rad(생성기.uniform(0, 1)))


생성기 = np.random.default_rng(0)
흔든_시뮬 = [무작위_물성(생성기) for _ in range(20)]
흔든_식별 = [식별_둘레(생성기) for _ in range(20)]
방법들 = {"(가) 시뮬에서만": (시뮬_물성, [시뮬_물성]), "(나) 식별한 모델에서": (식별_모델, [식별_모델]),
        "(다) 시뮬 + 무작위화": (시뮬_물성, 흔든_시뮬), "(라) 식별 + 좁은 무작위화": (식별_모델, 흔든_식별)}

궂은_현실들 = [현실_물성, replace(현실_물성, 끝_질량=0.85), replace(현실_물성, 끝_질량=0.85, 지연=3)]
print("방법                 | 이득         | 현실(평균 오차, 못 감) | 짐 0.3kg       | 짐 + 지연 30ms")
골라_둔 = {}
for 이름, (아는, 팔들) in 방법들.items():
    kp, kd = 가장_좋은_칸(점수표(아는, 팔들))
    골라_둔[이름] = (kp, kd, 아는)
    글 = []
    for 진짜 in 궂은_현실들:
        결과 = [성적(실행(제어기_만들기(kp, kd, 아는), 8.0, 진짜, 시드)) for 시드 in range(10)]
        글.append(f"{np.mean([r[0] for r in 결과]):5.2f}도, {sum(r[1] for r in 결과):2d}/40")
    print(f"{이름:16s} | kp={kp:3d}, kd={kd} | " + " | ".join(글))

그림, 칸들 = plt.subplots(2, 1, figsize=(8, 4.8), sharex=True)
for 이름 in ["(가) 시뮬에서만", "(라) 식별 + 좁은 무작위화"]:
    kp, kd, 아는 = 골라_둔[이름]
    기록 = 실행(제어기_만들기(kp, kd, 아는), 8.0, 현실_물성)
    for j in range(2):
        칸들[j].plot(기록["시각"], np.rad2deg(기록["참_각도"][:, j]), linewidth=1.1, label=이름)
for j, 관절 in enumerate(["어깨", "팔꿈치"]):
    칸들[j].plot(기록["시각"], [np.rad2deg(목표(t)[j]) for t in 기록["시각"]], "k--", linewidth=1, label="목표")
    칸들[j].set_ylabel(f"{관절} 각도(도)")
칸들[0].legend(fontsize=8, loc="upper left")
칸들[1].set_xlabel("시간(초)")
그림.tight_layout()
그림.savefig("practice_compare.png", dpi=200)
print("저장: practice_compare.png")
