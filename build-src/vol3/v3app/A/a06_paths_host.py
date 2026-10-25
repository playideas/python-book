"""내려받은 모델과 데이터가 어디에 쌓이는지, 얼마나 차지하는지 본다."""
import os
from pathlib import Path

import torch
from huggingface_hub import constants


def 짧게(경로: str | Path) -> str:
    """사용자 폴더 부분을 ~로 줄여서 보여 준다."""
    return str(경로).replace(str(Path.home()), "~")


def 크기_MB(폴더: Path) -> float:
    """폴더 안 파일 크기의 합(MB, 1MB = 2의 20제곱 바이트)."""
    return sum(f.stat().st_size for f in 폴더.rglob("*") if f.is_file()) / 2**20


데이터_폴더 = Path(os.environ.get("BOOK_DATA_DIR", "data"))
print("BOOK_DATA_DIR :", 짧게(데이터_폴더))
print("torch 캐시    :", 짧게(torch.hub.get_dir()))
print("Hugging Face  :", 짧게(constants.HF_HUB_CACHE))
for 이름 in ["fasterrcnn_mobilenet_v3_large_fpn-fb6a3cc7.pth", "keypointrcnn_resnet50_fpn_coco-fc266e95.pth"]:
    파일 = Path(torch.hub.get_dir()) / "checkpoints" / 이름
    print(f"  {이름:48s} {파일.stat().st_size / 2**20:7.1f}MB")
for 저장소 in ["HuggingFaceTB/SmolVLM-500M-Instruct", "google/owlv2-base-patch16-ensemble",
              "Qwen/Qwen2.5-0.5B-Instruct", "Qwen/Qwen2.5-1.5B-Instruct"]:
    폴더 = Path(constants.HF_HUB_CACHE) / ("models--" + 저장소.replace("/", "--")) / "blobs"
    print(f"  {저장소:48s} {크기_MB(폴더):7.1f}MB")
for 장 in ["ch10", "ch18"]:
    print(f"  BOOK_DATA_DIR/{장:34s} {크기_MB(데이터_폴더 / 장):7.1f}MB")
