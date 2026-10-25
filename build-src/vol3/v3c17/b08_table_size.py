import gymnasium as gym

# 관측 값 하나를 10칸으로만 나눠도 표의 칸 수는 10^(관측 수). 1초에 10억(10^9) 칸씩 한 번만 들러도
print(f"{'과제':27s}{'관측 수':>5s}  {'표의 칸 수':>9s}  한 번씩 들르는 데 걸리는 시간")
for 이름 in ["InvertedPendulum-v5", "InvertedDoublePendulum-v5", "Hopper-v5", "Ant-v5", "Humanoid-v5"]:
    차원 = gym.make(이름).observation_space.shape[0]
    지수 = 차원 - 9                                     # 걸리는 초 = 10^차원 / 10^9
    시간 = f"{10.0 ** 지수:g}초" if 지수 < 5 else f"10^{지수}초"
    print(f"{이름:27s}{차원:5d}  {'10^' + str(차원):>11s}  {시간}")
print("참고: 우주의 나이는 약 4×10^17초")
