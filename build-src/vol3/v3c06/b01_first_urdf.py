from urdf_parser_py.urdf import URDF

# 링크 둘과 그 둘을 잇는 회전 관절 하나: 3장 예제 팔의 첫 관절(허리)만 떼어 낸 것
글 = """
<robot name="waist_only">
  <link name="base_link"/>
  <link name="link1"/>
  <joint name="joint1" type="revolute">
    <parent link="base_link"/>
    <child link="link1"/>
    <origin xyz="0 0 0.1" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.14" upper="3.14" effort="10" velocity="2"/>
  </joint>
</robot>
"""
로봇 = URDF.from_xml_string(글)
관절 = 로봇.joints[0]
print("로봇 이름:", 로봇.name)
print("링크:", [링크.name for 링크 in 로봇.links])
print(f"관절 {관절.name}: {관절.type}, {관절.parent} → {관절.child}")
print("  고정 위치 xyz:", 관절.origin.xyz, "/ 회전축:", 관절.axis)
print("3장의 같은 관절: ('허리', [0, 0, 0.10], [0, 0, 1])")
