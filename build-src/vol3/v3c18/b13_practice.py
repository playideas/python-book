import os
from collections import Counter
from pathlib import Path

import numpy as np
import torch

from 모방환경 import 상자_범위, 높이
from 시연도구 import 굴리기, 시연_모으기, 시험_위치
from 정책도구 import 학습

데이터 = 시연_모으기(250)
관측, 행동, 에피소드 = 데이터["관측"], 데이터["행동"], 데이터["에피소드"]
생성기 = np.random.default_rng(3)
흔든_관측, 흔든_행동 = [], []
for i in range(50):                                   # 18.5절과 같은 '흔들며 시연' 50개
    o, a, _ = 굴리기(생성기.uniform(*상자_범위), 흔들림=0.004, 씨앗=500 + i)
    흔든_관측.append(o)
    흔든_행동.append(a)
다거_파일 = Path(os.environ.get("BOOK_DATA_DIR", "data")) / "ch18" / "dagger.pt"
정책들 = {"BC 시연 25": 학습(관측[에피소드 < 25], 행동[에피소드 < 25]),
         "BC 시연 200": 학습(관측[에피소드 < 200], 행동[에피소드 < 200]),
         "흔들며 시연 50": 학습(np.concatenate(흔든_관측), np.concatenate(흔든_행동)),
         "DAgger": torch.load(다거_파일, weights_only=False)}   # 18.5절에서 저장한 정책


def 결과(정책, 상자, 흔들림: float, 씨앗: int) -> str:
    """에피소드 하나를 굴리고 어떻게 끝났는지 한 단어로."""
    들었나 = [False]

    def 찍기(환경) -> None:
        들었나[0] |= 환경.데이터.body("box").xpos[2] > 높이 + 0.02     # 상자가 탁자에서 2cm 넘게 떴다

    _, _, 성공 = 굴리기(상자, 정책, 흔들림=흔들림, 씨앗=씨앗, 찍기=찍기)
    if 성공:
        return "성공"
    return "들었지만 실패" if 들었나[0] else "들지 못함"


시험 = 시험_위치(50)
for 흔들림 in [0.004, 0.006]:
    print(f"--- 흔들림 {흔들림} rad, 상자 위치 50곳")
    for 이름, 정책 in 정책들.items():
        세기 = Counter(결과(정책, p, 흔들림, i) for i, p in enumerate(시험))
        print(f"{이름:9s}  성공 {세기['성공'] / 50:4.0%}  (들지 못함 {세기['들지 못함']}, "
              f"들었지만 실패 {세기['들었지만 실패']})")
