from torchvision.models import detection

# 9장 9.8절의 검출기가 아는 이름표(가중치를 내려받지 않아도 읽을 수 있다)
범주 = detection.FasterRCNN_MobileNet_V3_Large_FPN_Weights.COCO_V1.meta["categories"]
이름들 = [이름 for 이름 in 범주 if 이름 not in ("__background__", "N/A")]
print(f"아는 이름 {len(이름들)}개:", ", ".join(이름들[40:48]), "...")
for 낱말 in ["cup", "bowl", "sports ball", "box", "red box", "blue bowl", "robot arm"]:
    print(f"  {낱말!r:14} → {'있음' if 낱말 in 이름들 else '없음'}")
