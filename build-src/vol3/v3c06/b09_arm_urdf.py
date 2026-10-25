import numpy as np
from urdf_parser_py.urdf import URDF as URDF읽기

from urdf기구학 import URDF_순기구학
from 팔도구 import 순기구학
from 팔URDF import URDF
from 회전도구 import 깔끔

글 = URDF()
print("만든 URDF:", len(글.splitlines()), "줄")
print("\n".join(글.splitlines()[8:14]))                  # joint1 부분만 보기

로봇 = URDF읽기.from_xml_string(글)
print("사슬:", 로봇.get_chain("base_link", "tip", links=False))

관절각 = np.deg2rad([30, 45, 60, 0, 45, 0])                 # 3장 3.3절의 자세
값들 = {f"joint{i + 1}": 각 for i, 각 in enumerate(관절각)}
print("URDF로 계산한 손끝:", 깔끔(URDF_순기구학(로봇, 값들, "tip")[:3, 3]))
print("3장 순기구학 손끝 :", 깔끔(순기구학(관절각)[-1][:3, 3]))

생성기 = np.random.default_rng(0)
최대_차이 = 0.0
for _ in range(100):                                       # 아무 자세 100개로 비교
    q = 생성기.uniform(-np.pi, np.pi, size=6)
    T = URDF_순기구학(로봇, {f"joint{i + 1}": 각 for i, 각 in enumerate(q)}, "tip")
    최대_차이 = max(최대_차이, np.abs(T - 순기구학(q)[-1]).max())
print(f"자세 100개, 4×4 행렬 최대 차이: {최대_차이:.1e}")
