"""10장: 사진 내려받기와 사전학습 자세 추정 모델(torchvision Keypoint R-CNN) 다루기."""
import os
import urllib.request
from pathlib import Path

import numpy as np
import torch
from torchvision.models.detection import KeypointRCNN_ResNet50_FPN_Weights, keypointrcnn_resnet50_fpn

데이터_폴더 = Path(os.environ.get("BOOK_DATA_DIR", "data")) / "ch10"

# 위키미디어 공용의 퍼블릭 도메인 사진(1910년대 미국 신문사·대학 사진)
사진_주소 = {
    "athlete_1913.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/"
                        "G.A._Dull%2C_Univ._of_Michigan%2C_athlete_LCCN2014680908.jpg/"
                        "960px-G.A._Dull%2C_Univ._of_Michigan%2C_athlete_LCCN2014680908.jpg",
    "runners_1912.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/"
                        "Runners_on_track_at_high_school_track_meet_1912_%283191653538%29.jpg/"
                        "960px-Runners_on_track_at_high_school_track_meet_1912_%283191653538%29.jpg",
}


def 사진_경로(이름: str) -> Path:
    """사진이 없으면 한 번 내려받고 경로를 돌려준다."""
    경로 = 데이터_폴더 / 이름
    if not 경로.exists():
        데이터_폴더.mkdir(parents=True, exist_ok=True)
        요청 = urllib.request.Request(사진_주소[이름], headers={"User-Agent": "python-book-example/1.0"})
        with urllib.request.urlopen(요청, timeout=60) as 응답:
            경로.write_bytes(응답.read())
    return 경로


def 장치_고르기() -> torch.device:
    """쓸 수 있는 가장 빠른 장치를 고른다(2권 4장)."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def 모델_불러오기(장치: torch.device) -> torch.nn.Module:
    """COCO로 학습한 Keypoint R-CNN. 처음 한 번은 가중치(약 226MB)를 내려받는다."""
    가중치 = KeypointRCNN_ResNet50_FPN_Weights.COCO_V1
    return keypointrcnn_resnet50_fpn(weights=가중치).eval().to(장치)


def 자세_찾기(모델: torch.nn.Module, 이미지: np.ndarray, 장치: torch.device) -> dict[str, np.ndarray]:
    """(높이, 너비, 3) uint8 이미지 → 사람마다 상자·점수·키포인트(17×2)·키포인트 점수."""
    텐서 = torch.from_numpy(이미지).permute(2, 0, 1).float().div(255).to(장치)
    with torch.no_grad():
        결과 = 모델([텐서])[0]
    return {"상자": 결과["boxes"].cpu().numpy(), "점수": 결과["scores"].cpu().numpy(),
            "키포인트": 결과["keypoints"][:, :, :2].cpu().numpy(),
            "키포인트_점수": 결과["keypoints_scores"].cpu().numpy()}
