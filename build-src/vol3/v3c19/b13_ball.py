import mujoco
import numpy as np

from 계획도구 import 규칙_계획
from 지시수행 import 계획_실행, 장면_읽기, 집게_요
from 지시장면 import 그릇_반지름, 그릇_중심, 장면_xml, 찍기
from 찾기도구 import 개방어휘검출기

검출기 = 개방어휘검출기()
for 방법, 요_정하기 in [("잰 요 그대로", lambda 이름, 장면: 장면[이름]["요_도"]), ("이웃을 피하는 요", 집게_요)]:
    모델 = mujoco.MjModel.from_xml_string(장면_xml())
    데이터 = mujoco.MjData(모델)
    장면 = 장면_읽기(모델, 데이터, 검출기, *찍기(모델, 데이터))
    닿은_곳: dict[str, str] = {}

    def 접촉_보기(작업) -> None:
        """손가락 패드가 무엇에 처음 닿았는지, 그때 어느 단계였는지 모은다."""
        for 접촉 in 데이터.contact[:데이터.ncon]:
            이름들 = {모델.geom(접촉.geom1).name, 모델.geom(접촉.geom2).name}
            if 패드 := {"pad_l", "pad_r"} & 이름들:
                닿은_곳.setdefault(f"{패드.pop()}-{(이름들 - {'pad_l', 'pad_r'}).pop()}", 작업.단계.value)

    결과 = 계획_실행(모델, 데이터, 규칙_계획("공을 그릇에 담아", list(장면)), 장면, 찍기=접촉_보기, 요_정하기=요_정하기)
    공 = 데이터.body("빨간 공").xpos
    print(f"[{방법}] 집게 요 {요_정하기('빨간 공', 장면):6.1f}도 → {결과[0][2]}, "
          f"공이 그릇 안? {np.linalg.norm(공[:2] - 그릇_중심) < 그릇_반지름}")
    print("   손가락이 처음 닿은 것:", ", ".join(f"{짝}({단계})" for 짝, 단계 in sorted(닿은_곳.items())))
