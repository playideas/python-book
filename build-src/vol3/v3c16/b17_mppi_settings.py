import mujoco
import numpy as np

from MPPI도구 import MPPI
from 진자장면 import 세운_자세_오차, 장면


def 해_보기(후보_수: int, 걸음_수: int) -> str:
    """6초 동안 흔들어 올리고, 언제 10도 안에 들었는지와 마지막 1초의 최대 오차를 돌려준다."""
    모델, 진짜 = 장면()
    제어기 = MPPI(모델, 후보_수=후보_수, 걸음_수=걸음_수)
    오차_도 = []
    for _ in range(600):
        진짜.ctrl[0] = 제어기.고르기(진짜)
        mujoco.mj_step(모델, 진짜)
        오차_도.append(np.rad2deg(abs(세운_자세_오차(진짜.qpos[0]))))
    오차_도 = np.array(오차_도)
    if 오차_도[-100:].max() > 10:
        return f"6초 안에 못 세움(마지막 1초 오차 {오차_도[-100:].min():.0f}~{오차_도[-100:].max():.0f}도)"
    return f"{(np.argmax(오차_도 < 10) + 1) * 모델.opt.timestep:.2f}초에 10도 안, 마지막 1초 최대 오차 {오차_도[-100:].max():.1f}도"


print("[내다보는 시간을 바꾸면] 후보 128개")
for 걸음_수 in [30, 60, 100, 150]:
    print(f"  {걸음_수 / 100:.1f}초 앞: {해_보기(128, 걸음_수)}")
print("[후보 수를 바꾸면] 1초 앞")
for 후보_수 in [8, 32, 128, 512]:
    print(f"  후보 {후보_수:3d}개: {해_보기(후보_수, 100)}")
