import numpy as np
import torch

from PPO도구 import 행위자비평가
from 그림도구 import 프레임격자
from 진자흔들기환경 import 진자흔들기환경
from 흔들기시험 import 평균_행동

모델 = 행위자비평가(3, 1)
모델.load_state_dict(torch.load("흔들기_정책.pt", weights_only=True))
정책 = 평균_행동(모델)
환경 = 진자흔들기환경()
상태, _ = 환경.reset(seed=1000)                            # 시험 첫 판과 같은 출발
찍을_걸음 = [0, 60, 120, 180, 240, 300, 360, 420]
프레임들, 제목들 = [], []
for 걸음 in range(421):
    if 걸음 in 찍을_걸음:
        프레임들.append(환경.render())
        제목들.append(f"{걸음 / 100:.1f}초  {np.rad2deg(환경.데이터.qpos[0]):.0f}도")
    상태, _, _, _, _ = 환경.step(정책(상태))
환경.close()
프레임격자(프레임들, 제목들, "ppo_swingup_frames.png", 열=4)
print("저장: ppo_swingup_frames.png")
