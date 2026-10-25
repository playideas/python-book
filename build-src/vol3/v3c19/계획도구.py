"""19장: 말로 한 지시를 정해진 기술의 순서(계획)로 바꾸고, 실행하기 전에 검사한다."""
import re

import numpy as np

from 잡기도구 import TCP_포즈, 역기구학, 집기_포즈
from 집게 import 손가락_최대
from 집고놓기 import 들기_높이
from 팔집게장면 import 집_자세

기술들 = {"집기": "물체 하나를 집어 든다", "놓기": "들고 있는 물체를 장소에 내려놓는다"}
놓을_곳들 = {"파란 그릇"}                     # 놓기의 대상이 될 수 있는 것
옮기는_말 = ("넣", "담", "놓", "올려", "옮겨")    # 규칙 계획기가 아는 동사의 앞부분
최대_단계 = 8
집을_수_있는_폭 = 2 * 손가락_최대 - 0.01         # 손가락을 다 벌려도 1cm 남아야 한다


def 이름_찾기(지시: str, 이름들: list[str]) -> list[str]:
    """지시에 나온 물체 이름을 나온 순서대로. '공'처럼 하나뿐인 물건은 색을 빼고 말해도 된다."""
    찾은것 = {지시.find(이름): 이름 for 이름 in 이름들 if 이름 in 지시}
    for 물건 in {이름.split()[-1] for 이름 in 이름들}:
        후보 = [이름 for 이름 in 이름들 if 이름.endswith(물건)]
        if len(후보) == 1 and 후보[0] not in 찾은것.values() and (위치 := 지시.find(물건)) >= 0:
            찾은것[위치] = 후보[0]
    return [찾은것[위치] for 위치 in sorted(찾은것)]


def 규칙_계획(지시: str, 이름들: list[str]) -> list[dict]:
    """'무엇(들)을 어디에 넣어' 꼴만 알아듣는 규칙 계획기. 모르면 빈 계획을 낸다."""
    if not any(말 in 지시 for 말 in 옮기는_말):
        return []
    나온것 = 이름_찾기(지시, 이름들)
    장소 = [이름 for 이름 in 나온것 if 이름 in 놓을_곳들 and re.search(이름.split()[-1] + r"\s*(에|안에|위에)", 지시)]
    물체 = [이름 for 이름 in 나온것 if 이름 not in 장소]
    if len(장소) != 1 or not 물체:
        return []
    return [단계 for 이름 in 물체 for 단계 in ({"기술": "집기", "대상": 이름}, {"기술": "놓기", "대상": 장소[0]})]


def 닿나(위치) -> bool:
    """팔이 위치에서 손가락을 아래로 향할 수 있고, 들기 높이까지도 닿는가(역기구학 남은 오차 1mm)."""
    for 위로 in (0.0, 들기_높이):
        T = 집기_포즈(np.asarray(위치) + [0, 0, 위로], 0.0)
        if np.linalg.norm(T[:3, 3] - TCP_포즈(역기구학(T, 집_자세, 반복=200))[:3, 3]) > 0.001:
            return False
    return True


def 계획_검사(계획, 장면: dict[str, dict]) -> list[str]:
    """계획이 지켜야 할 규칙을 모두 확인하고, 어긴 것을 글로 돌려준다. 빈 목록이면 통과."""
    if not isinstance(계획, list) or not 계획:
        return ["계획이 비었거나 목록이 아님"]
    if len(계획) > 최대_단계:
        return [f"단계가 {len(계획)}개로 너무 많음(최대 {최대_단계})"]
    문제들, 든_것 = [], None
    for 번호, 단계 in enumerate(계획, 1):
        기술, 대상 = (단계.get("기술"), 단계.get("대상")) if isinstance(단계, dict) else (None, None)
        if 기술 not in 기술들:
            문제들.append(f"{번호}단계: 모르는 기술 {기술!r}")
        elif 대상 not in 장면:
            문제들.append(f"{번호}단계: 장면에 없는 대상 {대상!r}")
        elif 기술 == "집기":
            if 든_것 is not None:
                문제들.append(f"{번호}단계: 이미 {든_것}을(를) 들고 있음")
            elif 대상 in 놓을_곳들 or 장면[대상]["폭"] > 집을_수_있는_폭:
                문제들.append(f"{번호}단계: {대상}은(는) 집을 수 없음(폭 {장면[대상]['폭'] * 100:.1f}cm)")
            elif not 닿나(장면[대상]["중심"]):
                문제들.append(f"{번호}단계: {대상}까지 팔이 닿지 않음")
            든_것 = 대상
        elif 대상 not in 놓을_곳들:
            문제들.append(f"{번호}단계: {대상}은(는) 놓을 곳이 아님")
        elif 든_것 is None:
            문제들.append(f"{번호}단계: 들고 있는 것이 없음")
        elif not 닿나(장면[대상]["중심"]):
            문제들.append(f"{번호}단계: {대상}까지 팔이 닿지 않음")
        else:
            든_것 = None
    if 든_것 is not None and not 문제들:
        문제들.append(f"끝까지 {든_것}을(를) 들고 있음")
    return 문제들
