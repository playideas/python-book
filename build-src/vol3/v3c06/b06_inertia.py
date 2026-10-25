from pathlib import Path

from urdf_parser_py.urdf import URDF

로봇 = URDF.from_xml_file(str(Path(__file__).with_name("두관절팔.urdf")))


def 원기둥_관성(질량: float, 반지름: float, 길이: float) -> tuple[float, float]:
    """꽉 찬 원기둥의 무게중심 기준 관성: (길이 방향 축, 그에 수직인 축)."""
    return 질량 * 반지름**2 / 2, 질량 * (3 * 반지름**2 + 길이**2) / 12


for 이름 in ["upper_arm", "forearm"]:
    링크 = 로봇.link_map[이름]
    모양 = 링크.collision.geometry                     # 부딪히는 모양(원기둥)의 치수
    관성 = 링크.inertial.inertia
    길이축, 옆축 = 원기둥_관성(링크.inertial.mass, 0.02, 모양.length)   # 막대 반지름 0.02m
    print(f"{이름}: 질량 {링크.inertial.mass}kg, 무게중심 {링크.inertial.origin.xyz}")
    print(f"  공식  ixx {길이축:.5f}, iyy=izz {옆축:.5f}")
    print(f"  URDF  ixx {관성.ixx:.5f}, iyy=izz {관성.iyy:.5f}")
