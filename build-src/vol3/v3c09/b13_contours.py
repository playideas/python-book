import cv2
import mujoco
import numpy as np
from PIL import Image

from 비전장면 import 장면_xml, 찍기
from 색찾기 import 물체_찾기, 색_범위

모델 = mujoco.MjModel.from_xml_string(장면_xml())
데이터 = mujoco.MjData(모델)
컬러, _ = 찍기(모델, 데이터, "머리")

찾은 = 물체_찾기(컬러)
표시 = 컬러.copy()
for 이름, 물체 in 찾은.items():
    u, v = 물체["중심"]
    x, y, w, h = cv2.boundingRect(물체["윤곽"])
    print(f"{이름}: 넓이 {물체['넓이']:6.0f}px, 중심 (u={u:6.1f}, v={v:6.1f}), 상자 x {x}~{x + w}, y {y}~{y + h}")
    cv2.drawContours(표시, [물체["윤곽"]], -1, (255, 0, 255), 2)
    cv2.drawMarker(표시, (round(u), round(v)), (0, 0, 0), cv2.MARKER_CROSS, 14, 2)
Image.fromarray(표시).save("contours.png")
print("저장: contours.png")

# 흔한 실수: RGB 사진을 OpenCV 기본 순서(BGR)인 줄 알고 바꾸면 빨강과 파랑이 뒤바뀐다
틀린_hsv = cv2.cvtColor(컬러, cv2.COLOR_BGR2HSV)
for 이름 in ["빨강", "파랑"]:
    개수 = sum(np.count_nonzero(cv2.inRange(틀린_hsv, np.array(a), np.array(b))) for a, b in 색_범위[이름])
    print(f"BGR로 착각했을 때 '{이름}' 범위에 든 픽셀: {개수}")
