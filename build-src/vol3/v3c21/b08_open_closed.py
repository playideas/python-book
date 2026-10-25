import mujoco
import numpy as np

from 정리로봇 import 정리로봇
from 책상인지 import 어느_상자
from 책상장면 import 무작위_배치, 장면_xml

물건들 = 무작위_배치(np.random.default_rng(0), {"빨강": 2, "초록": 2, "파랑": 1})


class 사람이_끼어드는_책상(정리로봇):
    """첫 물건을 옮긴 직후, 사람이 책상 위의 (받침에 가장 가까운) 물건 하나를 y로 8cm 밀어 둔다."""
    밀었나 = False

    def 행동(self, 물건, 물건들_):
        성공 = super().행동(물건, 물건들_)
        if not self.밀었나:
            남은 = [b for b in 물건들 if b["종류"] != "파랑" and 어느_상자(self.데이터.body(b["이름"]).xpos) is None]
            민_것 = min(남은, key=lambda b: np.linalg.norm(self.데이터.body(b["이름"]).xpos[:2]))
            주소 = self.모델.jnt_qposadr[self.모델.body(민_것["이름"]).jntadr[0]]   # freejoint의 x, y, z, 쿼터니언
            self.데이터.qpos[주소 + 1] += 0.08
            mujoco.mj_forward(self.모델, self.데이터)
            self.적기("사람", f"{민_것['이름']}을(를) y로 8cm 밂")
            self.밀었나 = True
        return 성공


for 다시_보기 in [False, True]:
    모델 = mujoco.MjModel.from_xml_string(장면_xml(물건들))
    데이터 = mujoco.MjData(모델)
    print(f"--- {'매번 다시 보기' if 다시_보기 else '처음 한 번만 보기'}")
    for 시각, 무엇, 메모 in 사람이_끼어드는_책상(모델, 데이터, 다시_보기=다시_보기).정리():
        print(f"{시각:5.1f}초  {무엇:5s} {메모}")
    print("   끝난 뒤:", ", ".join(f"{b['이름']} {어느_상자(데이터.body(b['이름']).xpos) or '책상'}"
                               f"(높이 {데이터.body(b['이름']).xpos[2]:.3f}m)" for b in 물건들 if b["종류"] != "파랑"))
