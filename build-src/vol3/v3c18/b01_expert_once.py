import mujoco

from 그림도구 import 프레임격자
from 모방환경 import 집고놓기환경, 최대_걸음, 제어_주기
from 전문가 import 목표_정하기, 전문가

환경 = 집고놓기환경([0.45, 0.15])
카메라 = mujoco.MjvCamera()
카메라.lookat[:] = [0.37, -0.05, 0.45]
카메라.distance, 카메라.azimuth, 카메라.elevation = 0.8, 200, -30
기록, 프레임들, 제목들 = [], [], []
with mujoco.Renderer(환경.모델, 240, 320) as 그리개:
    while 환경.걸음 < 최대_걸음 and not 환경.끝났나():
        단계 = 목표_정하기(환경)[2]
        if not 기록 or 기록[-1][1] != 단계:                 # 단계가 바뀐 걸음만 적고 찍는다
            기록.append((환경.걸음, 단계))
            if 단계 in ("다가가기", "쥐기", "옮기기", "놓기", "물러나기") and 단계 not in 제목들:
                그리개.update_scene(환경.데이터, camera=카메라)
                프레임들.append(그리개.render())
                제목들.append(단계)
        환경.한걸음(전문가(환경))
for 걸음, 단계 in 기록:
    print(f"{걸음:3d}걸음({걸음 * 제어_주기:4.2f}초)  {단계}")
print(f"끝: {환경.걸음}걸음, 성공 {환경.성공()}")
프레임격자(프레임들, 제목들, "expert_frames.png", 열=5)
print("저장: expert_frames.png")
