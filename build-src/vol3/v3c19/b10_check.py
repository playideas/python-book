import mujoco

from 계획도구 import 계획_검사, 규칙_계획
from 언어계획 import 언어계획기
from 지시수행 import 장면_읽기
from 지시장면 import 장면_xml, 찍기
from 찾기도구 import 개방어휘검출기

모델 = mujoco.MjModel.from_xml_string(장면_xml())
데이터 = mujoco.MjData(모델)
장면 = 장면_읽기(모델, 데이터, 개방어휘검출기(), *찍기(모델, 데이터))
계획기 = 언어계획기()


def 보기(계획) -> str:
    if not isinstance(계획, list):
        return str(계획)
    return " → ".join(f"{단계.get('기술')}({단계.get('대상')})" if isinstance(단계, dict) else str(단계) for 단계 in 계획)


for 지시 in ["빨간 상자를 파란 그릇에 넣어 줘", "노란 컵이랑 초록 상자를 그릇에 넣어", "공을 그릇에 담아",
             "파란 그릇을 빨간 상자 위에 올려"]:
    print(f"[{지시}]")
    for 누가, 계획 in [("규칙", 규칙_계획(지시, list(장면))), ("언어 모델", 계획기.계획(지시, list(장면))[0])]:
        문제들 = 계획_검사(계획, 장면)
        print(f"  {누가}: {보기(계획) or '(빈 계획)'}")
        print(f"    검사: {'통과' if not 문제들 else ' / '.join(문제들)}")
