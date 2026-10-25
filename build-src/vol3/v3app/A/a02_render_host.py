"""화면 없이 MuJoCo 장면을 찍을 수 있는지 확인한다."""
import mujoco
from mujoco import gl_context
from PIL import Image

장면 = """
<mujoco>
  <worldbody>
    <light pos="0 0 3"/>
    <camera name="앞" pos="0 -1 0.3" xyaxes="1 0 0 0 0.3 1"/>
    <geom type="plane" size="1 1 0.1" rgba="0.8 0.8 0.8 1"/>
    <geom type="sphere" pos="0 0 0.1" size="0.1" rgba="1 0 0 1"/>
  </worldbody>
</mujoco>
"""
모델 = mujoco.MjModel.from_xml_string(장면)
데이터 = mujoco.MjData(모델)
mujoco.mj_forward(모델, 데이터)
with mujoco.Renderer(모델, 120, 160) as 렌더러:
    렌더러.update_scene(데이터, "앞")
    사진 = 렌더러.render()
print("그림 그리기 방식:", gl_context.GLContext.__module__)
print("사진 모양:", 사진.shape, "/ 평균 밝기:", round(float(사진.mean()), 1))
빨간_픽셀 = (사진[:, :, 0] > 120) & (사진[:, :, 1] < 60)
print("빨간 공이 찍힌 픽셀 수:", int(빨간_픽셀.sum()))
Image.fromarray(사진).save("render_check.png")
print("저장: render_check.png")
