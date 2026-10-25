import mujoco
import numpy as np

from 정리로봇 import 정리로봇
from 책상장면 import 무작위_배치, 장면_xml

물건들 = 무작위_배치(np.random.default_rng(0), {"빨강": 2, "초록": 2, "파랑": 1})


class 선이_빠지는_카메라(정리로봇):
    """세 번째 사진부터 깊이 값이 오지 않는다(USB 선이 빠졌다고 치자)."""
    찍은_수 = 0

    def 사진(self):
        컬러, 깊이 = super().사진()
        self.찍은_수 += 1
        return (컬러, np.full_like(깊이, np.nan)) if self.찍은_수 >= 3 else (컬러, 깊이)


for 이름, 로봇_종류, 최대_시간 in [("카메라 고장", 선이_빠지는_카메라, 240.0), ("시간 한도 30초", 정리로봇, 30.0)]:
    모델 = mujoco.MjModel.from_xml_string(장면_xml(물건들))
    데이터 = mujoco.MjData(모델)
    기록 = 로봇_종류(모델, 데이터, 최대_시간=최대_시간).정리()
    print(f"--- {이름}")
    for 시각, 무엇, 메모 in 기록:
        print(f"{시각:5.1f}초  {무엇:5s} {메모}")
    print(f"   멈춘 자세(도): {np.rad2deg(데이터.qpos[:6]).round(0) + 0.0}, 손가락 너비 {데이터.sensor('width').data[0] * 100:.1f}cm")
