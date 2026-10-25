from pathlib import Path

import mujoco
import numpy as np

글 = Path(__file__).with_name("두관절팔.urdf").read_text()
경우들 = {
    "올바른 URDF": 글,
    "무게중심 origin을 빠뜨림": 글.replace('<origin xyz="0.2 0 0"/>\n      <mass', '<mass'),
    "질량을 g 단위로 적음": 글.replace('<mass value="0.5"/>', '<mass value="500"/>'),
}
for 이름, 내용 in 경우들.items():
    모델 = mujoco.MjModel.from_xml_string(내용)
    데이터 = mujoco.MjData(모델)
    데이터.qfrc_applied[0] = 0.2                        # 어깨에 0.2N·m 토크를 1초 동안
    while 데이터.time < 1.0:
        mujoco.mj_step(모델, 데이터)
    어깨, 팔꿈치 = np.rad2deg(데이터.qpos)
    print(f"{이름:14s}: 1초 뒤 어깨 {어깨:7.1f}도, 팔꿈치 {팔꿈치:6.1f}도")
