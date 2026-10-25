import matplotlib.pyplot as plt
import mujoco
import numpy as np

from 방장면 import 로봇_놓기, 방_만들기
from 주행데이터 import 시작_포즈

모델, 데이터 = 방_만들기()
로봇_놓기(모델, 데이터, 시작_포즈)
print("모양(geom) 수:", 모델.ngeom, "/ 몸체 수:", 모델.nbody, "/ mocap 몸체 수:", 모델.nmocap)

사진들 = []
with mujoco.Renderer(모델, 480, 600) as 렌더러:
    for 방위, 고도, 거리 in [(90, -90, 12.5), (60, -40, 11.5)]:    # 바로 위에서, 비스듬히
        카메라 = mujoco.MjvCamera()
        카메라.lookat[:] = [5, 4, 0]
        카메라.azimuth, 카메라.elevation, 카메라.distance = 방위, 고도, 거리
        렌더러.update_scene(데이터, camera=카메라)
        사진들.append(렌더러.render())
plt.imsave("room.png", np.hstack(사진들))
print("저장: room.png")
