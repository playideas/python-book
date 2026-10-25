import mujoco
import numpy as np

from 그림도구 import 프레임격자
from 잡기도구 import 요_고르기
from 집고놓기 import 집고놓기
from 팔집게장면 import 받침_위치, 상자_반크기, 장면_xml, 준비

상자, 상자_요 = np.array([0.4, 0.22]), 80.0
높이 = 받침_위치[2] + 상자_반크기[2]
놓을_곳 = np.array([0.3, -0.25, 높이])
모델 = mujoco.MjModel.from_xml_string(장면_xml(상자, 상자_요, 놓을_곳[:2]))
데이터 = mujoco.MjData(모델)
준비(모델, 데이터)

손가락_방향 = np.array([-np.sin(np.deg2rad(상자_요)), np.cos(np.deg2rad(상자_요))])  # 상자의 폭 방향
잰_곳들 = [상자 + 0.018 * 손가락_방향, 상자]                 # 첫 번째는 폭 방향으로 1.8cm 틀리게 잼

카메라 = mujoco.MjvCamera()
카메라.lookat[:] = [0.37, 0.05, 0.45]
카메라.distance, 카메라.azimuth, 카메라.elevation = 0.75, 200, -30
찍을_단계 = {"내려가기", "실패", "쥐기", "옮기기", "놓기"}
프레임들, 제목들 = [], []
with mujoco.Renderer(모델, 240, 320) as 그리개:
    for 시도, 잰_곳 in enumerate(잰_곳들, start=1):
        잡을_곳 = np.array([*잰_곳, 높이])
        q = 데이터.ctrl[:6].copy()
        작업 = 집고놓기(모델, 데이터, 잡을_곳, 요_고르기(잡을_곳, 상자_요, q),
                     놓을_곳, 요_고르기(놓을_곳, 90, q), 쥐는_힘=10.0)
        찍은_수 = [0]

        def 찍기(작업) -> None:
            """단계가 바뀐 직후에 한 장씩 찍는다."""
            if len(작업.기록) > 찍은_수[0]:
                찍은_수[0] = len(작업.기록)
                if 작업.단계.value in 찍을_단계:
                    그리개.update_scene(데이터, camera=카메라)
                    프레임들.append(그리개.render())
                    제목들.append(f"{시도}차 {작업.단계.value} ({데이터.time:.1f}초)")

        성공 = 작업.실행(최대_시간=데이터.time + 20, 찍기=찍기)
        print(f"--- {시도}차 시도: 잰 곳 {np.round(잰_곳, 3)} (참값 {상자}), 결과 {'성공' if 성공 else '실패'}")
        for 시각, 단계, 메모 in 작업.기록:
            print(f"  {시각:5.2f}초  {단계:5s} {메모}".rstrip())
        print("  상자 위치:", np.round(데이터.body("box").xpos, 3))
프레임격자(프레임들, 제목들, "pick_retry_frames.png")
print("저장: pick_retry_frames.png")
