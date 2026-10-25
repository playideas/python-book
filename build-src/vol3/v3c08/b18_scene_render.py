import matplotlib.pyplot as plt
import mujoco

from 바퀴장면 import 모델_만들기

모델 = 모델_만들기()
데이터 = mujoco.MjData(모델)
mujoco.mj_forward(모델, 데이터)
print("관절 수:", 모델.njnt, "/ 액추에이터:", [모델.actuator(i).name for i in range(모델.nu)])
print("센서:", [모델.sensor(i).name for i in range(모델.nsensor)])

카메라 = mujoco.MjvCamera()
카메라.lookat[:] = [0, 0, 0]
카메라.distance, 카메라.azimuth, 카메라.elevation = 8.0, 90, -50
with mujoco.Renderer(모델, 480, 640) as 렌더러:
    렌더러.update_scene(데이터, 카메라)
    plt.imsave("wheel_scene.png", 렌더러.render())
print("저장: wheel_scene.png")
