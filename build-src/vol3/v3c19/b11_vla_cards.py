import json
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download

# 모델 저장소의 정보(카드에 적힌 라이선스, 가중치 파일의 매개변수 수)를 읽는다. 가중치는 받지 않는다
api = HfApi()
for 저장소 in ["lerobot/smolvla_base", "lerobot/pi0_base", "openvla/openvla-7b"]:
    정보 = api.model_info(저장소)
    개수 = 정보.safetensors.total
    print(f"{저장소:22s} 라이선스 {정보.card_data.get('license'):6s} 매개변수 {개수 / 1e9:4.2f}B, "
          f"16비트로 {개수 * 2 / 1e9:4.1f}GB, 라이브러리 {정보.library_name}")

설정 = json.loads(Path(hf_hub_download("lerobot/smolvla_base", "config.json")).read_text())
print("\nSmolVLA 바탕 VLM:", 설정["vlm_model_name"])
for 이름, 특징 in {**설정["input_features"], **설정["output_features"]}.items():
    print(f"  {이름:28s} {특징['type']:7s} {특징['shape']}")
print("한 번에 내는 행동 수(chunk_size):", 설정["chunk_size"], "/ 사진 크기 맞춤:", 설정["resize_imgs_with_padding"])
