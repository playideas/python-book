import mujoco
import numpy as np
from scipy.spatial.transform import Rotation

from 잡기도구 import 요_고르기
from 집고놓기 import 집고놓기
from 팔집게장면 import 받침_위치, 상자_반크기, 장면_xml, 준비, 집_자세

상자, 상자_요 = (0.45, 0.15), 30.0
놓을_곳, 놓을_요 = np.array([0.3, -0.25, 받침_위치[2] + 상자_반크기[2]]), 90.0
모델 = mujoco.MjModel.from_xml_string(장면_xml(상자, 상자_요, 놓을_곳[:2]))
데이터 = mujoco.MjData(모델)
준비(모델, 데이터)

잡을_곳 = np.array([*상자, 받침_위치[2] + 상자_반크기[2]])   # 9장처럼 잰 상자 가운데(여기서는 정확히)
작업 = 집고놓기(모델, 데이터, 잡을_곳, 요_고르기(잡을_곳, 상자_요, 집_자세),
             놓을_곳, 요_고르기(놓을_곳, 놓을_요, 집_자세), 쥐는_힘=10.0)
성공 = 작업.실행()
for 시각, 단계, 메모 in 작업.기록:
    print(f"{시각:5.2f}초  {단계:5s} {메모}".rstrip())
놓인_곳 = 데이터.body("box").xpos
놓인_요 = Rotation.from_quat(데이터.body("box").xquat, scalar_first=True).as_euler("ZYX", degrees=True)[0]
print(f"성공: {성공}, 놓인 곳 {np.round(놓인_곳, 3)}, 목표와 {np.linalg.norm(놓인_곳[:2] - 놓을_곳[:2]) * 1000:.1f}mm, "
      f"요 {놓인_요:.1f}도")
