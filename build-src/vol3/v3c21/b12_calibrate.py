import mujoco
import numpy as np

from 책상인지 import 물건_찾기
from 책상장면 import 대기_자세, 물성, 장면_xml, 찍기
from 평가도구 import 요약, 한_판, 현실_물성

보정_자리 = np.array([0.40, 0.12, 0.42])            # 책상에 표시해 둔 자리: 노란 보정 블록(높이 4cm)의 가운데


def 카메라_치우침(p: 물성) -> np.ndarray:
    """노란 블록을 표시한 자리에 두고 재서, 잰 가운데 - 참 가운데를 돌려준다."""
    블록 = [{"이름": "보정", "종류": "노랑", "위치": 보정_자리[:2], "요": 0.0}]
    모델 = mujoco.MjModel.from_xml_string(장면_xml(블록, p))
    데이터 = mujoco.MjData(모델)
    데이터.qpos[:6] = 데이터.ctrl[:6] = 대기_자세
    mujoco.mj_forward(모델, 데이터)
    잰 = next(물건 for 물건 in 물건_찾기(*찍기(모델, 데이터, p)) if 물건["종류"] == "노랑")
    return 잰["중심"] - 보정_자리


print("시뮬 카메라의 치우침(mm):", (카메라_치우침(물성()) * 1000).round(1) + 0.0)
치우침 = 카메라_치우침(현실_물성)
print("현실 역할 카메라의 치우침(mm):", (치우침 * 1000).round(1) + 0.0)
print(요약("현실 역할 + 보정", [한_판(씨앗, 현실_물성, 보정=치우침) for 씨앗 in range(20)]))
