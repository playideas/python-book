"""10장: 3D 키포인트에 캡슐을 입혀 MuJoCo로 '합성 사람'을 그리는 장면."""
import numpy as np

from 골격도구 import 번호

피부, 셔츠, 바지 = "0.85 0.65 0.5 1", "0.2 0.4 0.75 1", "0.25 0.25 0.3 1"


def 캡슐(점들: np.ndarray, 가: str, 나: str, 굵기: float, 색: str) -> str:
    a, b = 점들[번호[가]], 점들[번호[나]]
    return (f'<geom type="capsule" fromto="{a[0]:.4f} {a[1]:.4f} {a[2]:.4f} {b[0]:.4f} {b[1]:.4f} {b[2]:.4f}" '
            f'size="{굵기}" rgba="{색}"/>')


def 사람_xml(점들: np.ndarray, 카메라_위치, 카메라_x축, 카메라_위축, 시야각_도: float) -> str:
    """키포인트 17×3을 받아 사람 모양 장면을 만든다. 카메라는 위치와 x축·위쪽 축으로 놓는다."""
    어깨_가운데 = (점들[번호["왼어깨"]] + 점들[번호["오른어깨"]]) / 2
    엉덩이_가운데 = (점들[번호["왼엉덩이"]] + 점들[번호["오른엉덩이"]]) / 2
    머리 = (점들[번호["왼귀"]] + 점들[번호["오른귀"]]) / 2 + [0.0, 0.0, 0.02]
    몸 = [캡슐(점들, "왼어깨", "오른어깨", 0.06, 셔츠), 캡슐(점들, "왼엉덩이", "오른엉덩이", 0.08, 바지)]
    몸.append(f'<geom type="capsule" fromto="{엉덩이_가운데[0]} 0 {엉덩이_가운데[2] + 0.05} '
             f'{어깨_가운데[0]} 0 {어깨_가운데[2] - 0.05}" size="0.15" rgba="{셔츠}"/>')
    몸.append(f'<geom type="capsule" fromto="0 0 {어깨_가운데[2]} 0 0 {머리[2] - 0.08}" size="0.045" rgba="{피부}"/>')
    몸.append(f'<geom type="ellipsoid" pos="{머리[0]} {머리[1]} {머리[2]}" size="0.095 0.08 0.11" rgba="{피부}"/>')
    for 쪽 in ["왼", "오른"]:
        몸.append(캡슐(점들, 쪽 + "어깨", 쪽 + "팔꿈치", 0.045, 셔츠))
        몸.append(캡슐(점들, 쪽 + "팔꿈치", 쪽 + "손목", 0.035, 피부))
        몸.append(캡슐(점들, 쪽 + "엉덩이", 쪽 + "무릎", 0.07, 바지))
        몸.append(캡슐(점들, 쪽 + "무릎", 쪽 + "발목", 0.055, 바지))
        손 = 점들[번호[쪽 + "손목"]]
        몸.append(f'<geom type="sphere" pos="{손[0]} {손[1]} {손[2]}" size="0.045" rgba="{피부}"/>')
        발 = 점들[번호[쪽 + "발목"]]
        몸.append(f'<geom type="box" pos="{발[0] + 0.06} {발[1]} 0.04" size="0.11 0.045 0.04" rgba="0.15 0.1 0.1 1"/>')
    x, 위 = 카메라_x축, 카메라_위축
    return f"""
<mujoco>
  <visual><global offwidth="640" offheight="480"/></visual>
  <asset>
    <texture type="skybox" builtin="gradient" rgb1="0.95 0.95 1" rgb2="0.6 0.7 0.8" width="256" height="256"/>
    <texture name="격자" type="2d" builtin="checker" rgb1="0.55 0.55 0.5" rgb2="0.75 0.75 0.7" width="256" height="256"/>
    <material name="바닥재" texture="격자" texrepeat="8 8"/>
  </asset>
  <worldbody>
    <light pos="2 1 4" dir="-0.4 -0.2 -1"/>
    <geom type="plane" size="5 5 0.1" material="바닥재"/>
    <camera name="cam" pos="{카메라_위치[0]} {카메라_위치[1]} {카메라_위치[2]}" fovy="{시야각_도}"
            xyaxes="{x[0]} {x[1]} {x[2]} {위[0]} {위[1]} {위[2]}"/>
    {chr(10).join(몸)}
  </worldbody>
</mujoco>"""
