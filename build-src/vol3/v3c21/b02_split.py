import cv2
import mujoco
import numpy as np

from 색찾기 import 물체_찾기, 색_마스크
from 책상인지 import 점구름, 위에서_나누기
from 책상장면 import 대기_자세, 무작위_배치, 장면_xml, 찍기

물건들 = 무작위_배치(np.random.default_rng(18), {"빨강": 2, "초록": 2, "파랑": 1})
모델 = mujoco.MjModel.from_xml_string(장면_xml(물건들))
데이터 = mujoco.MjData(모델)
데이터.qpos[:6] = 데이터.ctrl[:6] = 대기_자세
mujoco.mj_forward(모델, 데이터)
컬러, 깊이 = 찍기(모델, 데이터)
점들 = 점구름(깊이)

아홉장 = 물체_찾기(컬러)                                          # 9장: 색마다 가장 큰 덩어리 하나
for 종류 in ["빨강", "초록", "파랑"]:
    마스크 = 색_마스크(컬러, 종류)
    개수, _, 통계, _ = cv2.connectedComponentsWithStats(마스크)
    사진_덩어리 = int(np.sum(통계[1:, cv2.CC_STAT_AREA] >= 150))     # 사진에서 이어진 픽셀 덩어리
    위에서 = 위에서_나누기(점들[마스크 > 0])                          # 책상 위에서 내려다보고 나눈 덩어리
    print(f"{종류}: 실제 {sum(물건['종류'] == 종류 for 물건 in 물건들)}개 / 9장 방식 {int(종류 in 아홉장)}개 / "
          f"사진 덩어리 {사진_덩어리}개 / 위에서 나누면 {len(위에서)}개 {[len(덩어리) for 덩어리 in 위에서]}점")
