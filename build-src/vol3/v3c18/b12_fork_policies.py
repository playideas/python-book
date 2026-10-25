import matplotlib.pyplot as plt
import numpy as np
import torch

from 갈림길 import 굴리기, 반지름, 보폭, 시연, 장애물
from 여러답정책 import 혼합가우시안, 확산정책, 학습
from 정책도구 import 덩어리_만들기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

상태, 행동, 번호 = 시연(100)


def 덩어리_정책(모델, 묶음: int):
    """묶음 걸음마다 한 번 행동 덩어리를 뽑고, 그동안은 뽑은 것을 차례로 쓴다."""
    생성기, 남은, 걸음 = torch.Generator().manual_seed(0), None, [0]

    def 정책(p: np.ndarray) -> np.ndarray:
        nonlocal 남은
        if 걸음[0] % 묶음 == 0:
            남은 = 모델.뽑기(torch.tensor(p, dtype=torch.float32), 생성기).numpy().reshape(len(p), 묶음, 2)
        걸음[0] += 1
        return 남은[:, (걸음[0] - 1) % 묶음]
    return 정책


궤적들 = {"시연": [상태[번호 == i] for i in range(20)]}
print("정책               성공률  왼쪽으로  갈팡질팡(횟수)")
for 이름, 종류, 묶음 in [("혼합 가우시안", 혼합가우시안, 1), ("혼합 가우시안 덩어리", 혼합가우시안, 8),
                       ("확산", 확산정책, 1), ("확산 덩어리", 확산정책, 8)]:
    목표 = 덩어리_만들기(행동 / 보폭, 번호, 묶음).reshape(len(행동), -1)   # 묶음 걸음치 행동을 한 줄로
    모델 = 학습(종류, 상태, 목표)
    궤적, 성공 = 굴리기(덩어리_정책(모델, 묶음), 100)
    방향 = np.sign(np.diff(궤적[:, :25, 0], axis=1))        # 처음 25걸음 동안 x 방향이 바뀐 횟수
    갈팡질팡 = (np.diff(방향, axis=1) != 0).sum(1).mean()
    print(f"{이름:12s}  {성공.mean():5.0%}  {np.mean(궤적[:, 30, 0] < 0):7.0%}  {갈팡질팡:10.1f}")
    궤적들[이름] = 궤적[:20]

그림, 칸들 = plt.subplots(1, 5, figsize=(11, 3.2))
for 칸, (이름, 선들) in zip(칸들, 궤적들.items()):
    for 선 in 선들:
        칸.plot(선[:, 0], 선[:, 1], linewidth=0.8, alpha=0.7)
    칸.add_patch(plt.Circle(장애물, 반지름, color="gray"))
    칸.set_title(이름, fontsize=10)
    칸.set_xlim(-0.6, 0.6)
    칸.set_ylim(-0.1, 1.1)
    칸.set_aspect("equal")
    칸.set_xticks([])
    칸.set_yticks([])
그림.tight_layout()
그림.savefig("fork_policies.png", dpi=200)
print("저장: fork_policies.png")
