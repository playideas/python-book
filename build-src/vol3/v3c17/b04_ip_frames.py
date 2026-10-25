import gymnasium as gym

from 그림도구 import 프레임격자

환경 = gym.make("InvertedPendulum-v5", render_mode="rgb_array", width=240, height=240)
환경.action_space.seed(0)
for 판 in range(3):                                      # 앞의 무작위 정책과 같은 순서로 0~2번째 판을 지나서
    상태, _ = 환경.reset(seed=판)
    끝남 = 잘림 = False
    while not (끝남 or 잘림):
        상태, _, 끝남, 잘림, _ = 환경.step(환경.action_space.sample())
상태, _ = 환경.reset(seed=3)                              # 가장 오래 버틴 3번째 판(12걸음)을 찍는다
프레임들, 제목들 = [환경.render()], ["0걸음"]
for 걸음 in range(1, 13):
    상태, _, 끝남, 잘림, _ = 환경.step(환경.action_space.sample())
    if 걸음 % 4 == 0 or 끝남:
        프레임들.append(환경.render())
        제목들.append(f"{걸음}걸음  {상태[1]:+.2f}rad" + ("  끝" if 끝남 else ""))
    if 끝남:
        break
프레임격자(프레임들, 제목들, "ip_random.png", 열=len(프레임들))
print("저장: ip_random.png")
