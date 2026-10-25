import mujoco
import numpy as np

from 그림도구 import 프레임격자
from 세로팔 import 장면

모델 = mujoco.MjModel.from_xml_string(장면())
데이터 = mujoco.MjData(모델)
print("관절:", [모델.joint(i).name for i in range(모델.njnt)], "/ 토크 한계:", 모델.actuator_ctrlrange[:, 1])

# 팔을 수평으로 편 채 멈춰 있을 때와, 그 자세로 어깨가 돌고 있을 때의 qfrc_bias
for 이름, 각속도 in [("멈춤", [0.0, 0.0]), ("어깨가 3rad/s로 도는 중", [3.0, 0.0])]:
    데이터.qpos[:] = np.deg2rad([0, 45])
    데이터.qvel[:] = 각속도
    mujoco.mj_forward(모델, 데이터)
    print(f"(0도, 45도) {이름}: qfrc_bias = {np.round(데이터.qfrc_bias, 3)} N·m")

자세들_도 = [(-90, 0), (-30, 60), (20, 40), (45, -45)]
프레임들 = []
with mujoco.Renderer(모델, 240, 320) as 렌더러:
    for 자세 in 자세들_도:
        데이터.qpos[:] = np.deg2rad(자세)
        데이터.qvel[:] = 0.0
        mujoco.mj_forward(모델, 데이터)
        렌더러.update_scene(데이터, camera="side")
        프레임들.append(렌더러.render())
프레임격자(프레임들, [f"어깨 {a}도, 팔꿈치 {b}도" for a, b in 자세들_도], "arm_poses.png", 열=4)
print("저장: arm_poses.png")
