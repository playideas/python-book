import mujoco
import numpy as np

from 정리로봇 import 정리로봇
from 책상장면 import 무작위_배치, 장면_xml

물건들 = 무작위_배치(np.random.default_rng(3), {"빨강": 2, "초록": 2, "파랑": 1})
모델 = mujoco.MjModel.from_xml_string(장면_xml(물건들))
데이터 = mujoco.MjData(모델)
명령들 = []


class 받아_적는_로봇(정리로봇):
    def 지켜보기(self, 작업=None) -> None:
        명령들.append(self.데이터.ctrl.copy())                      # 제어 주기(100Hz)마다 보낸 명령


받아_적는_로봇(모델, 데이터).정리()
명령 = np.array(명령들)
한_번에_도 = np.rad2deg(np.abs(np.diff(명령[:, :6], axis=0)).max(axis=0))
SO101_이름 = ["shoulder_pan", "shoulder_lift", "elbow_flex", "(없음)", "wrist_flex", "wrist_roll"]
print(f"기록한 명령 {len(명령)}개({len(명령) * 0.01:.1f}초)")
for i, (이름, 실물) in enumerate(zip(["허리", "어깨", "팔꿈치", "손목1", "손목2", "손목3"], SO101_이름)):
    도 = np.round(np.rad2deg(명령[:, i]), 1) + 0.0
    print(f"{이름:4s} → {실물:13s}: {도.min():7.1f} ~ {도.max():6.1f}도, 10ms에 가장 크게 {한_번에_도[i]:.2f}도"
          f"(초당 {한_번에_도[i] * 100:.0f}도)")
print(f"집게 → gripper      : 너비 명령 {명령[:, 6].min() * 100:.1f} ~ {명령[:, 6].max() * 100:.1f}cm")
