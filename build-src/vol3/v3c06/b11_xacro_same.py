import subprocess
from pathlib import Path

import numpy as np
from urdf_parser_py.urdf import URDF as URDF읽기

from urdf기구학 import URDF_순기구학
from 팔URDF import URDF

xacro_글 = subprocess.run(["xacro", str(Path(__file__).with_name("예제팔.urdf.xacro"))],
                         capture_output=True, text=True, check=True).stdout
가 = URDF읽기.from_xml_string(xacro_글)       # xacro로 만든 것
나 = URDF읽기.from_xml_string(URDF())         # 파이썬(팔URDF.py)으로 만든 것

print("링크 이름이 같은가?", [l.name for l in 가.links] == [l.name for l in 나.links])
for 이름 in ["joint3", "joint6", "tip_joint"]:
    j가, j나 = 가.joint_map[이름], 나.joint_map[이름]
    print(f"{이름}: 위치 {j가.origin.xyz} == {j나.origin.xyz}, 축 {j가.axis} == {j나.axis}")
관성_차이 = max(abs(getattr(a.inertial.inertia, k) - getattr(b.inertial.inertia, k))
              for a, b in zip(가.links, 나.links) if a.inertial for k in ["ixx", "iyy", "izz"])
print(f"관성 값 최대 차이: {관성_차이:.1e}")

q = {f"joint{i + 1}": 각 for i, 각 in enumerate(np.deg2rad([30, 45, 60, 0, 45, 0]))}
print("손끝이 같은가?", np.allclose(URDF_순기구학(가, q, "tip"), URDF_순기구학(나, q, "tip")))
