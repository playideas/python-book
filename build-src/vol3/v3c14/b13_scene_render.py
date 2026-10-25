import matplotlib.pyplot as plt
import mujoco

from 주행장면 import 장면_만들기

모델, 데이터 = 장면_만들기((1.5, 1.5, 0.0))
카메라 = mujoco.MjvCamera()
카메라.lookat[:] = [5.0, 3.6, 0.0]
카메라.distance, 카메라.azimuth, 카메라.elevation = 12.0, 90, -62
with mujoco.Renderer(모델, 480, 640) as 렌더러:
    렌더러.update_scene(데이터, 카메라)
    plt.imsave("nav_scene.png", 렌더러.render())
print("저장: nav_scene.png")
