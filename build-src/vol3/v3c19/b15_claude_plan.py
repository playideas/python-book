import os

import anthropic
import mujoco

from 계획도구 import 계획_검사, 놓을_곳들
from 지시수행 import 계획_실행, 장면_읽기
from 지시장면 import 장면_xml, 찍기
from 찾기도구 import 개방어휘검출기

모델_ID = "claude-sonnet-5-5"           # 쓰는 모델은 여기 한 곳에서만 바꾼다
최대_왕복 = 6                            # Claude와 주고받는 횟수의 상한(1장의 감시견처럼)
도구_기술 = {"pick": "집기", "place": "놓기"}   # 도구 이름은 영문만 된다. 우리 기술 이름과 짝짓는다
시스템 = ("너는 로봇 팔의 작업 계획기다. 사람의 지시를 pick과 place 도구 호출의 순서로 바꾼다. "
         "도구 하나를 부를 때마다 로봇 쪽 검사 결과가 돌아온다. 거절되면 이유를 보고 계획을 고치거나, "
         "할 수 없는 지시면 도구를 부르지 말고 한두 문장으로 까닭을 말한다. 지시에 없는 일은 하지 않는다.")


def 도구_정의(장면: dict[str, dict]) -> list[dict]:
    """대상 이름을 장면에서 찾은 것으로만 고르게(enum) 해서, 없는 물체를 지어내지 못하게 한다."""
    def 도구(이름: str, 설명: str, 대상들: list[str]) -> dict:
        return {"name": 이름, "description": 설명, "strict": True,
                "input_schema": {"type": "object", "properties": {"target": {"type": "string", "enum": 대상들}},
                                 "required": ["target"], "additionalProperties": False}}
    return [도구("pick", "물체 하나를 집어 든다. 한 번에 하나만 들 수 있다.", [n for n in 장면 if n not in 놓을_곳들]),
            도구("place", "들고 있는 물체를 장소에 내려놓는다.", [n for n in 장면 if n in 놓을_곳들])]


def 장면_글(장면: dict[str, dict]) -> str:
    return "\n".join(f"- {이름}: 위치 ({잰['중심'][0]:.2f}, {잰['중심'][1]:.2f})m, 크기 {잰['길이'] * 100:.0f}×"
                     f"{잰['폭'] * 100:.0f}×{잰['높이'] * 100:.0f}cm" for 이름, 잰 in 장면.items())


def 클로드_계획(클라이언트, 지시: str, 장면: dict[str, dict]) -> tuple[list[dict], str]:
    """Claude가 도구를 부를 때마다 우리 규칙으로 검사해 받아들이거나 거절한다. (계획, Claude의 마지막 말)"""
    대화 = [{"role": "user", "content": f"장면(카메라로 잰 값):\n{장면_글(장면)}\n\n지시: {지시}"}]
    계획: list[dict] = []
    for _ in range(최대_왕복):
        응답 = 클라이언트.messages.create(model=모델_ID, max_tokens=16000, system=시스템,
                                       tools=도구_정의(장면), messages=대화)
        if 응답.stop_reason == "refusal":
            return [], "(Claude가 답하지 않음)"
        대화.append({"role": "assistant", "content": 응답.content})
        호출들 = [블록 for 블록 in 응답.content if 블록.type == "tool_use"]
        if not 호출들:
            return 계획, " ".join(블록.text for 블록 in 응답.content if 블록.type == "text")
        결과들 = []
        for 호출 in 호출들:
            단계 = {"기술": 도구_기술.get(호출.name), "대상": 호출.input.get("target")}
            문제들 = [문제 for 문제 in 계획_검사(계획 + [단계], 장면) if not 문제.startswith("끝까지")]
            print(f"   Claude: {호출.name}({단계['대상']}) → {'거절: ' + ' / '.join(문제들) if 문제들 else '받아들임'}")
            if not 문제들:
                계획.append(단계)
            결과들.append({"type": "tool_result", "tool_use_id": 호출.id, "is_error": bool(문제들),
                         "content": "거절: " + " / ".join(문제들) if 문제들 else "받아들임"})
        대화.append({"role": "user", "content": 결과들})
    return 계획, "(주고받기 상한에 닿음)"


if not (키 := os.environ.get("ANTHROPIC_API_KEY")):
    raise SystemExit("ANTHROPIC_API_KEY 환경 변수에 API 키를 넣고 다시 실행하세요.")
클라이언트 = anthropic.Anthropic(api_key=키)
검출기 = 개방어휘검출기()
for 지시 in ["빨간 상자를 파란 그릇에 넣어 줘", "초록 상자는 그릇에 넣지 마",
             "탁자 위 상자를 전부 그릇에 정리해 줘", "노란 컵을 그릇에 넣어"]:
    print(f"[{지시}]")
    모델 = mujoco.MjModel.from_xml_string(장면_xml())
    데이터 = mujoco.MjData(모델)
    장면 = 장면_읽기(모델, 데이터, 검출기, *찍기(모델, 데이터))
    계획, 말 = 클로드_계획(클라이언트, 지시, 장면)
    print(f"   Claude의 말: {말.strip() or '(없음)'}")
    if 계획 and not (문제들 := 계획_검사(계획, 장면)):                # 실행 직전에 계획 전체를 한 번 더 검사
        print("   실행:", [(물체, 메모) for 물체, _, 메모 in 계획_실행(모델, 데이터, 계획, 장면)])
    else:
        print("   실행하지 않음", 문제들 if 계획 else "(계획 없음)")
