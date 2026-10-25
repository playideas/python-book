import mujoco
import numpy as np

from 그림도구 import 프레임격자
from 실습장면 import XML, 목표_자세, 시작_자세, 충돌검사기

모델 = mujoco.MjModel.from_xml_string(XML())
데이터 = mujoco.MjData(모델)
print("관절 한계(도):", np.round(np.rad2deg(모델.jnt_range)).astype(int).tolist())

검사기 = 충돌검사기(여유=0.03)
for 이름, q in [("시작", 시작_자세), ("목표", 목표_자세)]:
    print(f"{이름} 자세 {np.rad2deg(q).round().astype(int)}도: 팔과 기둥 사이 {검사기.거리(q) * 1000:.0f}mm")
print("시작과 목표를 관절 공간에서 곧게 이으면 부딪히는가?", 검사기.선분_충돌(시작_자세, 목표_자세))

프레임들 = []
with mujoco.Renderer(모델, 240, 320) as 렌더러:
    for q in [시작_자세, 목표_자세]:
        데이터.qpos[:] = q
        mujoco.mj_forward(모델, 데이터)
        for 카메라 in ["overview", "top"]:
            렌더러.update_scene(데이터, camera=카메라)
            프레임들.append(렌더러.render())
프레임격자(프레임들, ["시작 자세", "시작 자세(위에서)", "목표 자세", "목표 자세(위에서)"], "arm_scene.png", 열=4)
print("저장: arm_scene.png")
