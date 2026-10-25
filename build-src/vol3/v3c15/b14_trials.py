import mujoco
import numpy as np
from scipy.spatial.transform import Rotation

from 잡기도구 import 요_고르기
from 집고놓기 import 집고놓기
from 팔집게장면 import 받침_위치, 상자_반크기, 장면_xml, 준비

생성기 = np.random.default_rng(0)
높이 = 받침_위치[2] + 상자_반크기[2]                         # 상자 가운데 높이
놓을_곳 = np.array([0.3, -0.25, 높이])


def 상자_요(데이터) -> float:
    return Rotation.from_quat(데이터.body("box").xquat, scalar_first=True).as_euler("ZYX", degrees=True)[0]


def 길이_폭_성분(데이터, 차이) -> np.ndarray:
    """수평 위치 차이를 상자의 길이 방향 성분과 폭 방향 성분으로 나눈다."""
    ψ = np.deg2rad(상자_요(데이터))
    return np.array([[np.cos(ψ), np.sin(ψ)], [-np.sin(ψ), np.cos(ψ)]]) @ 차이


def 재기(데이터) -> tuple[np.ndarray, float]:
    """9장처럼 카메라로 잰 상자 위치와 요. 참값에 9장 수준의 오차(1cm, 5도)를 섞는다."""
    위치 = 데이터.body("box").xpos[:2] + 생성기.normal(0, 0.01, 2)
    return np.array([*위치, 높이]), 상자_요(데이터) + 생성기.normal(0, 5)


결과 = []
for 번호 in range(20):
    상자, 요 = 생성기.uniform([0.3, -0.05], [0.5, 0.25]), 생성기.uniform(-90, 90)
    모델 = mujoco.MjModel.from_xml_string(장면_xml(상자, 요, 놓을_곳[:2]))
    데이터 = mujoco.MjData(모델)
    준비(모델, 데이터)
    이유들 = []
    for 시도 in range(1, 4):                                  # 실패하면 다시 재고 다시 시도, 세 번까지
        잡을_곳, 잰_요 = 재기(데이터)
        q = 데이터.ctrl[:6].copy()
        작업 = 집고놓기(모델, 데이터, 잡을_곳, 요_고르기(잡을_곳, 잰_요, q),
                     놓을_곳, 요_고르기(놓을_곳, 90, q), 쥐는_힘=10.0)
        폭_오차 = 길이_폭_성분(데이터, 잡을_곳[:2] - 데이터.body("box").xpos[:2])[1]
        if 작업.실행(최대_시간=데이터.time + 20):
            break
        이유들.append(f"{작업.기록[-1][2]}, 폭 방향으로 {폭_오차 * 1000:+.1f}mm 틀리게 잼")
    놓인_차이 = 데이터.body("box").xpos[:2] - 놓을_곳[:2]
    오차_mm = np.linalg.norm(놓인_차이) * 1000
    성공 = 오차_mm < 30                                        # 놓을 곳 표시(반지름 5cm) 안쪽 3cm
    결과.append((시도, 성공, 오차_mm, *np.abs(길이_폭_성분(데이터, 놓인_차이)) * 1000))
    print(f"{번호:2d}: 상자 {np.round(상자, 3)}, 요 {요:6.1f}도 → 시도 {시도}번, "
          f"{'성공' if 성공 else '실패'}, 놓인 오차 {오차_mm:5.1f}mm {' / '.join(이유들)}".rstrip())

시도들, 성공들, 오차들, 길이들, 폭들 = map(np.array, zip(*결과))
print(f"첫 시도에 성공: {np.sum(성공들 & (시도들 == 1))}/20, 다시 시도까지 성공: {성공들.sum()}/20")
print(f"놓인 오차: 평균 {오차들[성공들].mean():.1f}mm, 가장 클 때 {오차들[성공들].max():.1f}mm "
      f"(상자 길이 방향 평균 {길이들[성공들].mean():.1f}mm, 폭 방향 평균 {폭들[성공들].mean():.1f}mm)")
