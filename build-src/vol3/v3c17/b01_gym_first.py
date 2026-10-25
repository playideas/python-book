import gymnasium as gym

환경 = gym.make("InvertedPendulum-v5")             # 수레 위에 막대를 세우는 MuJoCo 과제
print(환경)                                          # make가 씌워 준 포장(래퍼)들
print("관측 공간:", 환경.observation_space)
print("행동 공간:", 환경.action_space)
print("한 걸음:", 환경.unwrapped.dt, "초 / 최대 걸음 수:", 환경.spec.max_episode_steps)

상태, 정보 = 환경.reset(seed=0)
print("처음 상태 [수레 위치, 막대 각도, 수레 속도, 막대 각속도]:", 상태.round(4))
다음_상태, 보상, 끝남, 잘림, 정보 = 환경.step([0.5])    # 수레를 오른쪽으로 조금 민다
print("한 걸음 뒤:", 다음_상태.round(4))
print("보상:", 보상, "/ terminated:", 끝남, "/ truncated:", 잘림)
