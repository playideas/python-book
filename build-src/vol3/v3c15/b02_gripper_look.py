import mujoco
import numpy as np
from PIL import Image

from 집게시험장면 import 만들기, 흘려보내기

모델, 데이터 = 만들기()
카메라 = mujoco.MjvCamera()
카메라.lookat[:] = [0, 0, 0.46]
카메라.distance, 카메라.azimuth, 카메라.elevation = 0.36, 160, -12

사진들 = []
with mujoco.Renderer(모델, 300, 300) as 그리개:
    for 너비, 들기 in [(0.08, 0.0), (0.0, 0.0), (0.0, 0.06)]:     # 벌리고 → 쥐고 → 6cm 들기
        데이터.ctrl[모델.actuator("grip").id] = 너비
        데이터.ctrl[모델.actuator("lift").id] = 들기
        흘려보내기(모델, 데이터, 1.0)
        그리개.update_scene(데이터, camera=카메라)
        사진들.append(그리개.render())
        print(f"너비 명령 {너비 * 100:.0f}cm, 들기 {들기 * 100:.0f}cm → 잰 너비 {데이터.sensor('width').data[0] * 100:.2f}cm, "
              f"접촉 센서 {데이터.sensor('touch_l').data[0]:.2f}N / {데이터.sensor('touch_r').data[0]:.2f}N")
Image.fromarray(np.hstack(사진들)).save("gripper.png")
print("저장: gripper.png")
