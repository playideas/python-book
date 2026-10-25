from pathlib import Path

import numpy as np
from urdf_parser_py.urdf import URDF

로봇 = URDF.from_xml_file(str(Path(__file__).with_name("두관절팔.urdf")))
print("뿌리 링크:", 로봇.get_root())
print("바닥 → 손끝 사슬:", 로봇.get_chain(로봇.get_root(), "tip"))

for 링크 in 로봇.links:
    가진것 = [이름 for 이름, 값 in [("visual", 링크.visual), ("collision", 링크.collision),
                                ("inertial", 링크.inertial)] if 값 is not None]
    질량 = f", 질량 {링크.inertial.mass}kg" if 링크.inertial else ""
    print(f"링크 {링크.name:9s}: {', '.join(가진것) or '(빈 링크)'}{질량}")

for 관절 in 로봇.joints:
    줄 = f"관절 {관절.name:9s}: {관절.type:8s} 위치 {관절.origin.xyz}"
    if 관절.limit and 관절.type != "fixed":
        범위 = np.round(np.rad2deg([관절.limit.lower, 관절.limit.upper]), 1)
        줄 += f", 축 {관절.axis}, 범위 {범위[0]}~{범위[1]}도"
    print(줄)
