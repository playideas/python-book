import mujoco
import numpy as np

from MPPI도구 import MPPI
from 그림도구 import 프레임격자
from 진자장면 import 장면

모델, 진짜 = 장면()
제어기 = MPPI(모델, 후보_수=128, 걸음_수=100)              # 앞 실험과 같은 설정, 같은 씨앗
찍을_걸음 = {0: "0.0초", 70: "0.7초", 145: "1.45초", 230: "2.3초", 290: "2.9초", 400: "4.0초"}
프레임들, 제목들 = [], []
with mujoco.Renderer(모델, 240, 240) as 렌더러:
    for 걸음 in range(401):
        if 걸음 in 찍을_걸음:
            mujoco.mj_forward(모델, 진짜)
            렌더러.update_scene(진짜, camera="옆")
            프레임들.append(렌더러.render())
            제목들.append(f"{찍을_걸음[걸음]}  {np.rad2deg(진짜.qpos[0]):.0f}도")
        진짜.ctrl[0] = 제어기.고르기(진짜)
        mujoco.mj_step(모델, 진짜)
프레임격자(프레임들, 제목들, "swingup_frames.png", 열=6)
print("저장: swingup_frames.png")
