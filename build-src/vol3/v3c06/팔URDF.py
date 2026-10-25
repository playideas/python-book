"""팔도구.py의 예제_팔을 URDF 글로 옮긴다. 3장 팔모델.py(MJCF)의 URDF판이다."""
from 팔도구 import 손끝_위치, 예제_팔

반지름 = 0.02         # 링크 막대의 반지름(m)
선밀도 = 2.0          # 링크 1m당 질량(kg/m). 예제용으로 정한 값


def 원기둥_관성(질량: float, 길이: float) -> tuple[float, float, float]:
    """z축 방향으로 꽉 찬 원기둥의 무게중심 기준 관성 (ixx, iyy, izz)."""
    옆 = 질량 * (3 * 반지름**2 + 길이**2) / 12
    return 옆, 옆, 질량 * 반지름**2 / 2


def 링크(이름: str, 길이: float) -> str:
    """길이만큼 z축 방향으로 뻗은 막대 링크. 보이는 모양·부딪히는 모양·질량을 함께 적는다."""
    질량 = 선밀도 * 길이
    ixx, iyy, izz = 원기둥_관성(질량, 길이)
    가운데 = f'<origin xyz="0 0 {길이 / 2:g}"/>'
    모양 = f'<geometry><cylinder radius="{반지름}" length="{길이:g}"/></geometry>'
    return (f'  <link name="{이름}">\n'
            f'    <visual>{가운데}{모양}</visual>\n'
            f'    <collision>{가운데}{모양}</collision>\n'
            f'    <inertial>{가운데}<mass value="{질량:g}"/>\n'
            f'      <inertia ixx="{ixx:.6g}" ixy="0" ixz="0" iyy="{iyy:.6g}" iyz="0" izz="{izz:.6g}"/></inertial>\n'
            f'  </link>')


def 관절(이름: str, 부모: str, 자식: str, 위치, 축=None) -> str:
    """축이 있으면 회전 관절(revolute), 없으면 고정 관절(fixed)."""
    xyz = " ".join(f"{값:g}" for 값 in 위치)
    줄들 = [f'  <joint name="{이름}" type="{"revolute" if 축 else "fixed"}">',
          f'    <parent link="{부모}"/><child link="{자식}"/>',
          f'    <origin xyz="{xyz}" rpy="0 0 0"/>']
    if 축:
        줄들 += [f'    <axis xyz="{" ".join(f"{값:g}" for 값 in 축)}"/>',
               '    <limit lower="-3.14159" upper="3.14159" effort="10" velocity="2"/>']
    return "\n".join(줄들 + ["  </joint>"])


def URDF(팔=예제_팔, 손끝=손끝_위치) -> str:
    """바닥(base_link) → link1 … link6 → 손끝(tip). 관절 i는 link(i-1)과 link(i)를 잇는다."""
    길이들 = [위치[2] for _, 위치, _ in 팔] + [손끝[2]]     # 이 팔은 모든 링크가 z축 방향
    부분들 = [링크("base_link", 길이들[0])]
    for i, (_, 위치, 축) in enumerate(팔, start=1):
        부모 = "base_link" if i == 1 else f"link{i - 1}"
        부분들 += [관절(f"joint{i}", 부모, f"link{i}", 위치, 축), 링크(f"link{i}", 길이들[i])]
    부분들 += [관절("tip_joint", f"link{len(팔)}", "tip", 손끝), '  <link name="tip"/>']
    return '<?xml version="1.0"?>\n<robot name="arm6">\n' + "\n".join(부분들) + "\n</robot>\n"
