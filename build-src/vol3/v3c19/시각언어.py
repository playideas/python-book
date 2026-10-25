"""19장: 작은 비전-언어 모델(SmolVLM)에게 사진을 보여 주고 묻는다."""
import numpy as np
import torch
from PIL import Image
from transformers import AutoModelForImageTextToText, AutoProcessor

모델_이름 = "HuggingFaceTB/SmolVLM-500M-Instruct"     # Apache-2.0, 약 5억 매개변수


def 불러오기() -> tuple:
    처리기 = AutoProcessor.from_pretrained(모델_이름)
    모델 = AutoModelForImageTextToText.from_pretrained(모델_이름, dtype=torch.float32).eval()   # CPU
    return 처리기, 모델


def 묻기(처리기, 모델, 사진: np.ndarray, 질문: str, 최대_토큰: int = 60) -> tuple[str, int]:
    """사진 한 장과 질문 하나. (답, 모델에 들어간 토큰 수)를 돌려준다. 늘 같은 답이 나오게 탐욕 디코딩."""
    대화 = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": 질문}]}]
    글 = 처리기.apply_chat_template(대화, add_generation_prompt=True)
    입력 = 처리기(text=글, images=[Image.fromarray(사진)], return_tensors="pt")
    with torch.inference_mode():
        출력 = 모델.generate(**입력, max_new_tokens=최대_토큰, do_sample=False)
    길이 = 입력["input_ids"].shape[1]
    return 처리기.batch_decode(출력[:, 길이:], skip_special_tokens=True)[0].strip(), 길이
