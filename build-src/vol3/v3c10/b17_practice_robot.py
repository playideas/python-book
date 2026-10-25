import matplotlib.pyplot as plt
import mujoco
import numpy as np

from 따라하기 import 사람_팔_각, 오른팔_복원, 저역통과
from 로봇팔장면 import XML
from 사람장면 import 사람_xml
from 손흔들기데이터 import 시간, 잰_픽셀, 참_키포인트, 초당_프레임, 카메라들

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# 앞 블록과 같은 흐름: 픽셀 → 삼각측량 → 관절 각도 → 어깨만 거르기
잰_각 = np.array([사람_팔_각(*팔) for 팔 in 오른팔_복원(카메라들, 잰_픽셀(잡음_px=2.0))])
목표_각 = np.column_stack([저역통과(잰_각[:, 0], 0.5), 잰_각[:, 1]])

모델 = mujoco.MjModel.from_xml_string(XML)
데이터 = mujoco.MjData(모델)
데이터.qpos[:2] = 목표_각[0]                       # 첫 자세에서 출발
실제_각, 프레임들 = [], []
찍을_프레임 = [15, 30, 45, 60]
with mujoco.Renderer(모델, 240, 320) as 렌더러:
    for k in range(len(시간)):
        데이터.ctrl[:] = 목표_각[k]                 # 30Hz로 새 목표를 보낸다
        데이터.qpos[2:4] = 목표_각[k]               # 반투명 팔은 목표 자세를 그대로 보여 준다
        while 데이터.time < (k + 1) / 초당_프레임:
            mujoco.mj_step(모델, 데이터)
        실제_각.append(데이터.qpos[:2].copy())
        if k in 찍을_프레임:
            mujoco.mj_forward(모델, 데이터)
            렌더러.update_scene(데이터, camera="정면")
            프레임들.append(렌더러.render())
실제_각 = np.array(실제_각)

차이 = np.rad2deg(실제_각 - 목표_각)
print("로봇이 목표를 따라간 RMS 오차(도) 어깨·팔꿈치:", np.sqrt(np.mean(차이**2, axis=0)).round(2))
print("가장 크게 벌어졌을 때(도):", np.abs(차이).max(axis=0).round(2))

# 같은 순간의 사람을 뒤에서 찍는다(뒤에서 보면 사람의 오른팔이 화면 오른쪽에 온다)
참값 = 참_키포인트()
그림, 칸들 = plt.subplots(2, 4, figsize=(9, 3.9))
for j, (프레임, k) in enumerate(zip(프레임들, 찍을_프레임)):
    장면 = mujoco.MjModel.from_xml_string(사람_xml(참값[k], [-2.6, 0, 1.3], [0, -1, 0], [0, 0, 1], 45))
    상태 = mujoco.MjData(장면)
    mujoco.mj_forward(장면, 상태)
    with mujoco.Renderer(장면, 240, 320) as 렌더러:
        렌더러.update_scene(상태, camera="cam")
        칸들[0, j].imshow(렌더러.render())
    칸들[1, j].imshow(프레임)
    칸들[0, j].set_title(f"{시간[k]:.1f}초", fontsize=10)
for 칸 in 칸들.ravel():
    칸.axis("off")
그림.tight_layout()
그림.savefig("practice_robot.png", dpi=200)
print("저장: practice_robot.png")
