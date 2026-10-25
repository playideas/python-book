"""9.5절: HSV 색 범위로 물체를 찾는 도구."""
import cv2
import numpy as np

# OpenCV의 HSV: 색상 H는 0~179(도를 반으로 나눈 값), 채도 S와 밝기 V는 0~255
색_범위 = {
    "빨강": [((0, 120, 40), (8, 255, 255)), ((172, 120, 40), (179, 255, 255))],   # 빨강은 0도 양쪽에 걸친다
    "초록": [((45, 120, 40), (85, 255, 255))],
    "파랑": [((100, 120, 40), (130, 255, 255))],
    "노랑": [((20, 120, 40), (35, 255, 255))],
}


def 색_마스크(컬러_rgb: np.ndarray, 이름: str) -> np.ndarray:
    """RGB 사진에서 이름의 색 범위에 드는 픽셀을 255, 나머지를 0으로 표시한다."""
    hsv = cv2.cvtColor(컬러_rgb, cv2.COLOR_RGB2HSV)                 # MuJoCo 사진은 RGB 순서
    마스크 = np.zeros(hsv.shape[:2], np.uint8)
    for 아래, 위 in 색_범위[이름]:
        마스크 |= cv2.inRange(hsv, np.array(아래), np.array(위))
    return cv2.morphologyEx(마스크, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))   # 작은 티끌 지우기


def 물체_찾기(컬러_rgb: np.ndarray, 최소_넓이: int = 50) -> dict[str, dict]:
    """색마다 가장 큰 덩어리의 윤곽, 넓이, 중심 픽셀 (u, v), 덩어리 마스크를 돌려준다."""
    결과 = {}
    for 이름 in 색_범위:
        윤곽들, _ = cv2.findContours(색_마스크(컬러_rgb, 이름), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not 윤곽들:
            continue
        윤곽 = max(윤곽들, key=cv2.contourArea)
        모멘트 = cv2.moments(윤곽)
        if 모멘트["m00"] < 최소_넓이:
            continue
        덩어리 = np.zeros(컬러_rgb.shape[:2], np.uint8)
        cv2.drawContours(덩어리, [윤곽], -1, 255, thickness=cv2.FILLED)
        결과[이름] = {"윤곽": 윤곽, "넓이": 모멘트["m00"], "덩어리": 덩어리 > 0,
                     "중심": (모멘트["m10"] / 모멘트["m00"], 모멘트["m01"] / 모멘트["m00"])}
    return 결과
