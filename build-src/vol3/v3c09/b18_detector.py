import mujoco
import torch
from torchvision.models import detection

from 비전장면 import 장면_xml, 찍기

모델 = mujoco.MjModel.from_xml_string(장면_xml())
데이터 = mujoco.MjData(모델)
컬러, _ = 찍기(모델, 데이터, "머리")

가중치 = detection.FasterRCNN_MobileNet_V3_Large_FPN_Weights.COCO_V1   # COCO 데이터셋 80범주로 학습
검출기 = detection.fasterrcnn_mobilenet_v3_large_fpn(weights=가중치, box_score_thresh=0.05).eval()
범주 = 가중치.meta["categories"]

사진 = torch.from_numpy(컬러).permute(2, 0, 1)                   # (높이, 너비, 3) → (3, 높이, 너비)
with torch.inference_mode():
    결과 = 검출기([가중치.transforms()(사진)])[0]               # CPU에서 돌려 결과를 고정한다
print(f"점수 0.05 넘는 검출 {len(결과['scores'])}개")
for 상자, 번호, 점수 in zip(결과["boxes"][:6], 결과["labels"][:6], 결과["scores"][:6]):
    x1, y1, x2, y2 = 상자.round().int().tolist()
    print(f"{범주[번호]:12s} 점수 {점수:.2f}, 상자 x {x1}~{x2}, y {y1}~{y2}")
