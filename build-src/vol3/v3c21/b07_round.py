import mujoco
import numpy as np

from 그림도구 import 프레임격자
from 정리로봇 import 정리로봇
from 책상장면 import 무작위_배치, 장면_xml, 찍기

물건들 = 무작위_배치(np.random.default_rng(3), {"빨강": 2, "초록": 2, "파랑": 1})
모델 = mujoco.MjModel.from_xml_string(장면_xml(물건들))
데이터 = mujoco.MjData(모델)
카메라 = mujoco.MjvCamera()
카메라.lookat[:], 카메라.distance, 카메라.azimuth, 카메라.elevation = [0.3, -0.05, 0.42], 1.25, 200, -50
프레임들, 제목들 = [], []


class 찍어_두는_로봇(정리로봇):
    def 사진(self):
        """머리 카메라로 볼 때마다 비스듬한 카메라로도 한 장 남긴다."""
        with mujoco.Renderer(self.모델, 300, 400) as 그리개:
            그리개.update_scene(self.데이터, camera=카메라)
            프레임들.append(그리개.render())
        제목들.append(f"{len(제목들) + 1}번째 보기 ({self.데이터.time:.1f}초)")
        return super().사진()


로봇 = 찍어_두는_로봇(모델, 데이터)
for 시각, 무엇, 메모 in 로봇.정리():
    print(f"{시각:5.1f}초  {무엇:5s} {메모}")
print("본 횟수:", len(프레임들))
프레임들.append(찍기(모델, 데이터)[0])                    # 마지막으로 머리 카메라가 본 사진도 함께
제목들.append("머리 카메라의 마지막 사진")
프레임격자(프레임들, 제목들, "tidy_round.png", 열=3)
print("저장: tidy_round.png")
