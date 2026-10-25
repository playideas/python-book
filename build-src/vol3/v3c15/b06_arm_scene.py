import mujoco
import numpy as np
from PIL import Image

from 잡기도구 import TCP_포즈
from 팔집게장면 import 장면_xml, 준비

모델 = mujoco.MjModel.from_xml_string(장면_xml())
데이터 = mujoco.MjData(모델)
print("관절 수(nq):", 모델.nq, "= 팔 6 + 손가락 2 + 상자 자유 관절 7")

# 3장의 순기구학(손끝을 TCP로 바꾼 것)과 MuJoCo의 tcp 사이트가 같은 곳을 가리키나?
생성기 = np.random.default_rng(0)
차이 = []
for _ in range(100):
    q = 생성기.uniform(-np.pi, np.pi, size=6)
    데이터.qpos[:6] = q
    mujoco.mj_forward(모델, 데이터)
    T = TCP_포즈(q)
    차이.append(max(np.abs(데이터.site("tcp").xpos - T[:3, 3]).max(),
                  np.abs(데이터.site("tcp").xmat.reshape(3, 3) - T[:3, :3]).max()))
print(f"TCP 포즈 최대 차이: {max(차이):.1e}")

준비(모델, 데이터)                                       # 출발 자세, 손가락은 활짝
print("출발 자세의 TCP 위치:", np.round(데이터.site("tcp").xpos, 3) + 0.0)
print("TCP의 z축(손가락이 뻗은 쪽):", np.round(데이터.site("tcp").xmat.reshape(3, 3)[:, 2], 3) + 0.0)
# gravcomp가 관절에 보태는 힘(qfrc_gravcomp)은 12장 12.9절의 qfrc_bias(멈춰 있을 때 = 중력)와 같을까?
print("qfrc_bias    :", np.round(데이터.qfrc_bias[:6], 3) + 0.0)
print("qfrc_gravcomp:", np.round(데이터.qfrc_gravcomp[:6], 3) + 0.0)

카메라 = mujoco.MjvCamera()
카메라.lookat[:] = [0.3, 0.0, 0.5]
카메라.distance, 카메라.azimuth, 카메라.elevation = 1.3, 145, -28
with mujoco.Renderer(모델, 360, 480) as 그리개:
    그리개.update_scene(데이터, camera=카메라)
    Image.fromarray(그리개.render()).save("arm_scene.png")
print("저장: arm_scene.png")
