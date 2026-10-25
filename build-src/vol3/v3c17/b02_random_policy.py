import gymnasium as gym

환경 = gym.make("InvertedPendulum-v5")
환경.action_space.seed(0)
for 판 in range(5):
    상태, _ = 환경.reset(seed=판)
    보상합, 걸음 = 0.0, 0
    while True:
        행동 = 환경.action_space.sample()                 # 아무렇게나 민다
        상태, 보상, 끝남, 잘림, _ = 환경.step(행동)
        보상합 += 보상
        걸음 += 1
        if 끝남 or 잘림:
            break
    print(f"{판}번째 판: {걸음:2d}걸음({걸음 * 환경.unwrapped.dt:.2f}초), 보상 합 {보상합:.0f}, "
          f"막대 각도 {상태[1]:+.3f}rad, terminated={끝남}, truncated={잘림}")
