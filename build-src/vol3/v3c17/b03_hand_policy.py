import gymnasium as gym
import numpy as np


def 해_보기(이득: list[float]) -> str:
    """관측에 이득을 곱해 더한 값으로 미는 '손으로 짠 정책'을 한 판 돌려 본다."""
    환경 = gym.make("InvertedPendulum-v5")
    상태, _ = 환경.reset(seed=0)
    for 걸음 in range(1, 2000):
        행동 = np.clip([np.dot(이득, 상태)], -3, 3)        # 정책: 상태 → 행동
        상태, 보상, 끝남, 잘림, _ = 환경.step(행동)
        if 끝남 or 잘림:
            return (f"{걸음}걸음에서 끝, terminated={끝남}, truncated={잘림}, "
                    f"수레 위치 {상태[0]:+.2f}m, 막대 각도 {상태[1]:+.3f}rad")


# 관측 순서: [수레 위치, 막대 각도, 수레 속도, 막대 각속도]
print("막대만 보는 PD     :", 해_보기([0, 10, 0, 1]))
print("수레 자리도 보는 정책:", 해_보기([1, 10, 1, 1]))
