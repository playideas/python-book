from torchvision.models.detection import KeypointRCNN_ResNet50_FPN_Weights

from 골격도구 import 뼈, 키포인트_이름

# 가중치 정보(meta)만 읽는다. 가중치 파일은 아직 내려받지 않는다
영어_이름 = KeypointRCNN_ResNet50_FPN_Weights.COCO_V1.meta["keypoint_names"]
for i in range(0, 17, 4):
    print("  ".join(f"{j:2d} {영어_이름[j]:14s}" for j in range(i, min(i + 4, 17))).rstrip())

# 영어 이름을 우리말로 옮겨 골격도구.py의 순서와 같은지 확인
낱말 = {"left": "왼", "right": "오른", "nose": "코", "eye": "눈", "ear": "귀", "shoulder": "어깨",
      "elbow": "팔꿈치", "wrist": "손목", "hip": "엉덩이", "knee": "무릎", "ankle": "발목"}
옮김 = ["".join(낱말[조각] for 조각 in 이름.split("_")) for 이름 in 영어_이름]
print("순서가 같은가?", 옮김 == 키포인트_이름)
print("키포인트", len(키포인트_이름), "개 / 뼈", len(뼈), "개")
