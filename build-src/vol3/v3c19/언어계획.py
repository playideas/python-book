"""19장: 작은 언어 모델(2권 14장의 Qwen2.5)에게 지시를 계획(JSON 목록)으로 바꾸게 한다."""
import json

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from 계획도구 import 기술들


class 언어계획기:
    def __init__(self, 이름: str = "Qwen/Qwen2.5-0.5B-Instruct"):     # Apache-2.0
        self.토크나이저 = AutoTokenizer.from_pretrained(이름)
        self.모델 = AutoModelForCausalLM.from_pretrained(이름, dtype=torch.float32).eval()

    def 시스템_글(self, 이름들: list[str]) -> str:
        기술_글 = ", ".join(f"{기술}(대상): {설명}" for 기술, 설명 in 기술들.items())
        return ("너는 로봇 팔의 작업 계획기다. 사람의 지시를 아래 기술의 순서로 바꾼다.\n"
                f"기술: {기술_글}\n장면에 있는 것: {', '.join(이름들)}\n"
                'JSON 목록으로만 답한다. 예: [{"기술": "집기", "대상": "초록 상자"}, {"기술": "놓기", "대상": "파란 그릇"}]')

    def 계획(self, 지시: str, 이름들: list[str]) -> tuple[list | None, str]:
        """(읽어 낸 계획 또는 None, 모델이 쓴 글 그대로). 탐욕 디코딩이라 늘 같은 답이 나온다."""
        대화 = [{"role": "system", "content": self.시스템_글(이름들)}, {"role": "user", "content": 지시}]
        입력 = self.토크나이저.apply_chat_template(대화, add_generation_prompt=True, return_tensors="pt",
                                               return_dict=True)
        with torch.inference_mode():
            출력 = self.모델.generate(**입력, max_new_tokens=120, do_sample=False)
        글 = self.토크나이저.decode(출력[0, 입력["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        try:
            return json.loads(글), 글
        except json.JSONDecodeError:
            return None, 글
