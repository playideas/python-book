import mujoco
import numpy as np
from PIL import Image

from 팔URDF import URDF

# URDF를 MjSpec(고칠 수 있는 모델 설계도)으로 읽고, URDF에 없는 바닥·조명·색을 덧붙인다
설계 = mujoco.MjSpec.from_string(URDF())
설계.worldbody.add_light(pos=[0, -1, 2], dir=[0, 0.5, -1])
설계.worldbody.add_geom(type=mujoco.mjtGeom.mjGEOM_PLANE, size=[1, 1, 0.1], rgba=[0.9, 0.9, 0.9, 1])
for 모양 in 설계.geoms:
    if 모양.type == mujoco.mjtGeom.mjGEOM_CYLINDER:
        모양.rgba = [0.8, 0.5, 0.2, 1]
설계.body("link6").add_site(name="tip", pos=[0, 0, 0.05], size=[0.015, 0, 0], rgba=[0.1, 0.3, 0.9, 1])
설계.worldbody.add_geom(type=mujoco.mjtGeom.mjGEOM_SPHERE, size=[0.02, 0, 0], pos=[0.484, -0.155, 0.09],
                       rgba=[0.9, 0.1, 0.1, 1])                # 6.7절에서 손목 카메라가 본 컵
모델 = 설계.compile()
데이터 = mujoco.MjData(모델)

카메라 = mujoco.MjvCamera()
카메라.lookat[:] = [0.25, 0.0, 0.25]
카메라.distance, 카메라.azimuth, 카메라.elevation = 1.3, -100, -20
사진들 = []
with mujoco.Renderer(모델, 400, 400) as 그리개:
    for 관절각_도 in [[30, 45, 60, 0, 45, 0], [-20, 30, 70, 0, 60, 0]]:
        데이터.qpos[:] = np.deg2rad(관절각_도)
        mujoco.mj_forward(모델, 데이터)
        그리개.update_scene(데이터, camera=카메라)
        사진들.append(그리개.render())
        print(f"{관절각_도} → 손끝 {np.round(데이터.site('tip').xpos, 3) + 0.0}")
Image.fromarray(np.hstack(사진들)).save("arm6_urdf_mujoco.png")
print("저장: arm6_urdf_mujoco.png")
