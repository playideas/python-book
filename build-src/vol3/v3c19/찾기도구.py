"""19장: 글로 지정한 물체를 사진에서 찾고(OWLv2), 깊이로 3차원 위치·방향·크기를 잰다."""
import mujoco
import numpy as np
import torch
from PIL import Image
from transformers import AutoProcessor, Owlv2ForObjectDetection

from 지시장면 import R_광학_mj, 높이, 너비, 탁자_높이

검출기_이름 = "google/owlv2-base-patch16-ensemble"     # Apache-2.0, 약 1.5억 매개변수


class 개방어휘검출기:
    def __init__(self):
        self.처리기 = AutoProcessor.from_pretrained(검출기_이름)
        self.모델 = Owlv2ForObjectDetection.from_pretrained(검출기_이름).eval()   # CPU: 결과를 고정한다

    def 찾기(self, 사진: np.ndarray, 글들: list[str], 문턱: float = 0.1) -> dict[str, tuple]:
        """글마다 가장 점수 높은 상자 하나: {글: (점수, [x1, y1, x2, y2])}. 문턱 아래면 빠진다."""
        그림 = Image.fromarray(사진)
        입력 = self.처리기(text=[글들], images=그림, return_tensors="pt")
        with torch.inference_mode():
            출력 = self.모델(**입력)
        결과 = self.처리기.post_process_grounded_object_detection(
            출력, threshold=문턱, target_sizes=[(그림.height, 그림.width)], text_labels=[글들])[0]
        찾은것: dict[str, tuple] = {}
        for 상자, 점수, 글 in zip(결과["boxes"].tolist(), 결과["scores"].tolist(), 결과["text_labels"]):
            if 글 not in 찾은것 or 점수 > 찾은것[글][0]:
                찾은것[글] = (점수, 상자)
        return 찾은것


def 점구름(모델: mujoco.MjModel, 데이터: mujoco.MjData, 깊이: np.ndarray) -> np.ndarray:
    """깊이 사진의 픽셀마다 세계 기준 3차원 점(높이×너비×3). 9장의 역투영과 변환 사슬."""
    f = (높이 / 2) / np.tan(np.deg2rad(모델.cam("머리").fovy[0]) / 2)
    v, u = np.indices(깊이.shape)
    점_광학 = np.stack([(u - (너비 - 1) / 2) / f * 깊이, (v - (높이 - 1) / 2) / f * 깊이, 깊이], axis=-1)
    R_세계_광학 = 데이터.cam("머리").xmat.reshape(3, 3) @ R_광학_mj
    return 점_광학 @ R_세계_광학.T + 데이터.cam("머리").xpos


def 상자_재기(점들: np.ndarray, 상자, 반경: float = 0.06) -> dict | None:
    """검출 상자 안의 점에서 물체 윗면을 골라 가운데·요·크기를 잰다(15장 15.3절의 주성분 분석).
    반경: 가운데에서 이만큼(m) 안의 점만 쓴다. 상자에 걸친 이웃 물체의 점을 덜어 낸다."""
    x1, y1, x2, y2 = (int(round(값)) for 값 in 상자)
    안 = 점들[max(y1, 0):y2, max(x1, 0):x2].reshape(-1, 3)
    위 = 안[안[:, 2] > 탁자_높이 + 0.01]                       # 탁자보다 1cm 넘게 높은 점
    if len(위) < 20:
        return None
    가운데 = np.median(위[:, :2], axis=0)
    위 = 위[np.linalg.norm(위[:, :2] - 가운데, axis=1) < 반경]
    윗면_높이 = np.percentile(위[:, 2], 90)
    윗면 = 위[위[:, 2] > 윗면_높이 - 0.005][:, :2]
    중심 = 윗면.mean(axis=0)
    _, 고유벡터 = np.linalg.eigh(np.cov((윗면 - 중심).T))
    긴축 = 고유벡터[:, 1]
    투영 = (윗면 - 중심) @ 고유벡터
    return {"중심": np.array([*중심, (탁자_높이 + 윗면_높이) / 2]),    # 윗면과 탁자의 한가운데 높이
            "요_도": float(np.rad2deg(np.arctan2(긴축[1], 긴축[0]))),
            "길이": float(np.ptp(투영[:, 1])), "폭": float(np.ptp(투영[:, 0])),
            "높이": float(윗면_높이 - 탁자_높이)}
