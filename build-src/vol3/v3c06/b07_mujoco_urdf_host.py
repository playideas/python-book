from pathlib import Path

import mujoco

글 = Path(__file__).with_name("두관절팔.urdf").read_text()
모델 = mujoco.MjModel.from_xml_string(글)               # MuJoCo는 URDF도 바로 읽는다
print("몸체:", [모델.body(i).name for i in range(모델.nbody)])
print("관절:", [모델.joint(i).name for i in range(모델.njnt)], "/ 범위(rad):", 모델.jnt_range[1].round(3))
print("모양(geom) 수:", 모델.ngeom, "/ 질량(kg):", 모델.body_mass.round(3))

# visual을 버리지 말고, 고정된 몸체도 합치지 말라고 MuJoCo 전용 설정을 끼워 넣으면
설정 = '<robot name="two_link_arm">\n  <mujoco><compiler discardvisual="false" fusestatic="false"/></mujoco>'
모델2 = mujoco.MjModel.from_xml_string(글.replace('<robot name="two_link_arm">', 설정))
print("설정 뒤 몸체:", [모델2.body(i).name for i in range(모델2.nbody)], "/ 모양 수:", 모델2.ngeom)

# 위팔의 inertial을 빠뜨리면?
빠뜨림 = 글.split("<inertial>", 1)[0] + 글.split("</inertial>", 1)[1]
모델3 = mujoco.MjModel.from_xml_string(빠뜨림)
위팔 = 모델3.body("upper_arm")
print(f"위팔 inertial 없음 → 질량 {위팔.mass[0]:.3f}kg, 관성 {위팔.inertia.round(5)}")
