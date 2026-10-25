import mujoco

from 그림도구 import 프레임격자
from 모방환경 import 제어_주기
from 시연도구 import 굴리기, 시연_모으기, 시험_위치
from 전문가 import 목표_정하기
from 정책도구 import 학습

데이터 = 시연_모으기(250)
학습_칸 = 데이터["에피소드"] < 200
정책 = 학습(데이터["관측"][학습_칸], 데이터["행동"][학습_칸])

카메라 = mujoco.MjvCamera()
카메라.lookat[:] = [0.4, 0.0, 0.45]
카메라.distance, 카메라.azimuth, 카메라.elevation = 0.7, 200, -30
프레임들, 제목들 = [], []
그리개 = None


def 찍기(환경) -> None:
    """1.2초마다 한 장. 제목에는 전문가가 그 상태를 어느 단계로 읽는지 적는다."""
    global 그리개
    if 그리개 is None:
        그리개 = mujoco.Renderer(환경.모델, 240, 320)
    if 환경.걸음 % 60 == 0:
        그리개.update_scene(환경.데이터, camera=카메라)
        프레임들.append(그리개.render())
        제목들.append(f"{환경.걸음 * 제어_주기:.1f}초 {목표_정하기(환경)[2]}")
        print(f"{환경.걸음 * 제어_주기:4.1f}초  전문가가 읽은 단계: {목표_정하기(환경)[2]:5s} "
              f"너비 {환경.데이터.sensor('width').data[0] * 100:.1f}cm, "
              f"TCP에서 본 상자 {(환경.관측()[10:] * 100).round(1)}cm")


_, _, 성공 = 굴리기(시험_위치(50)[0], 정책, 흔들림=0.004, 씨앗=0, 찍기=찍기)
그리개.close()
print("성공:", 성공)
프레임격자(프레임들[:6], 제목들[:6], "bc_failure_frames.png")
print("저장: bc_failure_frames.png")
