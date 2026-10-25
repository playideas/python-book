import mujoco
import numpy as np

from 비전장면 import K_만들기, R_로봇_머리, 머리_fovy, 머리_위치_로봇, 장면_xml, 찍기, 축_글자

기준선 = 0.06                                     # 두 눈 사이 거리(m)
가운데 = np.array([0, 0, 0.75]) + 머리_위치_로봇     # 로봇은 회전 없이 (0, 0, 0.75)에 서 있다
오른쪽 = R_로봇_머리[:, 0]                           # 광학 x축 = 사진의 오른쪽 방향
눈 = ""
for 이름, 부호 in [("왼눈", -0.5), ("오른눈", 0.5)]:
    위치 = " ".join(f"{x:.6f}" for x in 가운데 + 부호 * 기준선 * 오른쪽)
    눈 += f'<camera name="{이름}" pos="{위치}" xyaxes="{축_글자(R_로봇_머리)}" fovy="{머리_fovy}"/>\n'

모델 = mujoco.MjModel.from_xml_string(장면_xml(눈))
데이터 = mujoco.MjData(모델)
f = K_만들기(머리_fovy)[0, 0]

열_평균 = {}
for 이름 in ["왼눈", "오른눈"]:
    컬러, 깊이 = 찍기(모델, 데이터, 이름)
    R, G, B = (컬러[..., i].astype(int) for i in range(3))
    빨강 = (R > 100) & (G < 60) & (B < 60)                 # 빨간 컵 픽셀(간단한 규칙)
    행들, 열들 = np.nonzero(빨강)
    열_평균[이름] = 열들.mean()
    print(f"{이름}: 빨간 픽셀 {빨강.sum()}개, 가운데 열 {열들.mean():.1f}, 행 {행들.mean():.1f}")
    if 이름 == "왼눈":
        깊이_정답 = np.median(깊이[빨강])

시차 = 열_평균["왼눈"] - 열_평균["오른눈"]
print(f"시차 d = {시차:.2f}px → 거리 Z = f·B/d = {f * 기준선 / 시차:.3f}m (깊이 영상 중앙값 {깊이_정답:.3f}m)")
for Z in [0.5, 1.0, 2.0, 4.0]:
    d = f * 기준선 / Z
    print(f"Z = {Z:.1f}m: 시차 {d:5.1f}px, 시차를 0.5px 틀리면 거리 오차 {f * 기준선 / (d - 0.5) - Z:6.3f}m")
