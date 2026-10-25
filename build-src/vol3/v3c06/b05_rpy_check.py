import subprocess

import numpy as np
from scipy.spatial.transform import Rotation

from tf도구 import 상태_발행기, 연결

롤, 피치, 요 = np.deg2rad([10, 20, 30])      # 2장 2.4절과 같은 값
# 고정 관절 하나에 origin rpy만 적은 URDF
urdf = f"""<robot name="rpy_test">
  <link name="base_link"/><link name="tip"/>
  <joint name="j" type="fixed"><parent link="base_link"/><child link="tip"/>
    <origin xyz="0 0 0" rpy="{롤} {피치} {요}"/></joint>
</robot>"""
# 같은 세 숫자를 명령줄 도구 static_transform_publisher에도 준다
정적_발행 = subprocess.Popen(
    ["ros2", "run", "tf2_ros", "static_transform_publisher", "--roll", str(롤), "--pitch", str(피치),
     "--yaw", str(요), "--frame-id", "base_link", "--child-frame-id", "camera"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
with 상태_발행기(urdf), 연결() as 팔:
    R_urdf = 팔.변환("base_link", "tip")[:3, :3]
    R_명령줄 = 팔.변환("base_link", "camera")[:3, :3]
정적_발행.terminate()
정적_발행.wait()

후보 = {"Rz(요) @ Ry(피치) @ Rx(롤)": Rotation.from_euler("z", 요).as_matrix()
        @ Rotation.from_euler("y", 피치).as_matrix() @ Rotation.from_euler("x", 롤).as_matrix(),
        "scipy 소문자 'xyz'(고정 축)": Rotation.from_euler("xyz", [롤, 피치, 요]).as_matrix(),
        "scipy 대문자 'XYZ'(움직이는 축)": Rotation.from_euler("XYZ", [롤, 피치, 요]).as_matrix()}
for 이름, R in 후보.items():
    print(f"{이름:24s}: URDF {np.allclose(R_urdf, R)!s:5s} / static_transform_publisher {np.allclose(R_명령줄, R)}")
