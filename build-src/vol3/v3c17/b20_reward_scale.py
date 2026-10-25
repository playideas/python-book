import gymnasium as gym
import torch

from PPO도구 import GAE, 모으기, 행위자비평가
from 진자흔들기환경 import 진자흔들기환경

for 배율 in [1.0, 0.1]:
    torch.manual_seed(0)
    환경 = gym.wrappers.TransformReward(진자흔들기환경(), lambda r: 배율 * r)   # 보상에 배율을 곱하는 래퍼
    모델 = 행위자비평가(3, 1)
    자료, _, _, _ = 모으기(환경, 모델, 2048, 환경.reset(seed=0)[0])
    with torch.no_grad():
        가치 = 모델.가치(자료["상태"])
        이점 = GAE(자료["보상"], 가치, 모델.가치(자료["다음_상태"]), 자료["경계"], 0.99, 0.95)
    목표_가치 = 이점 + 가치
    분포 = 모델.정책.분포(자료["상태"])
    정책_손실 = -(분포.log_prob(자료["행동"]).sum(-1) * (이점 - 이점.mean()) / 이점.std()).mean()
    가치_손실 = 0.5 * ((모델.가치(자료["상태"]) - 목표_가치) ** 2).mean()
    (정책_손실 + 가치_손실).backward()
    정책_크기 = torch.cat([p.grad.flatten() for p in 모델.정책.parameters()]).norm().item()
    가치_크기 = torch.cat([p.grad.flatten() for p in 모델.가치망.parameters()]).norm().item()
    print(f"보상 × {배율}: 목표 가치 평균 {목표_가치.mean():8.1f}, 기울기 크기 정책 {정책_크기:.3f} / 가치 {가치_크기:6.1f}"
          f" → 0.5로 자르면 정책 몫 {정책_크기 * 0.5 / max(0.5, (정책_크기**2 + 가치_크기**2) ** 0.5):.5f}")
