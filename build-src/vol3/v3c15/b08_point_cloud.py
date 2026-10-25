import mujoco
import numpy as np

from 팔집게장면 import 받침_위치, 상자_반크기, 장면_xml

모델 = mujoco.MjModel.from_xml_string(장면_xml(상자_위치=(0.45, 0.15), 상자_요_도=30))
데이터 = mujoco.MjData(모델)
데이터.qpos[:6] = np.deg2rad([180, 30, 90, 0, 60, 0])   # 팔을 뒤로 돌려 카메라 앞을 비운다
mujoco.mj_forward(모델, 데이터)

높이, 너비 = 240, 320
with mujoco.Renderer(모델, 높이, 너비) as 그리개:
    그리개.enable_depth_rendering()
    그리개.update_scene(데이터, camera="top")
    깊이 = 그리개.render()                               # 픽셀마다 광학 z(m), 9장 9.4절

# 9장의 역투영: 픽셀 (u, v)와 깊이 Z → 광학 좌표 (X, Y, Z)
f = (높이 / 2) / np.tan(np.deg2rad(모델.cam("top").fovy[0]) / 2)
v, u = np.indices(깊이.shape)
X, Y = (u - (너비 - 1) / 2) / f * 깊이, (v - (높이 - 1) / 2) / f * 깊이
# 이 카메라는 바로 아래를 본다: 광학 x = 세계 x, 광학 y = 세계 -y, 광학 z = 세계 -z
점들 = np.stack([X, -Y, -깊이], axis=-1).reshape(-1, 3) + 데이터.cam("top").xpos
탁자 = 받침_위치[2]
위 = 점들[(점들[:, 2] > 탁자 + 0.01) & (점들[:, 0] > 0.15)]   # 작업 영역(팔 받침 앞)에서 탁자보다 1cm 넘게 높은 점
윗면_높이 = np.percentile(위[:, 2], 90)
윗면 = 위[위[:, 2] > 윗면_높이 - 0.005][:, :2]            # 윗면에 찍힌 점들의 (x, y)
print(f"탁자 위 점 {len(위)}개 중 윗면 점 {len(윗면)}개")

가운데 = 윗면.mean(axis=0)
고유값, 고유벡터 = np.linalg.eigh(np.cov((윗면 - 가운데).T))  # 주성분 분석: 퍼진 방향 찾기
긴축 = 고유벡터[:, 1]                                     # 가장 크게 퍼진 방향 = 긴 변
요_도 = np.rad2deg(np.arctan2(긴축[1], 긴축[0]))
투영 = (윗면 - 가운데) @ 고유벡터
길이, 폭 = np.ptp(투영[:, 1]), np.ptp(투영[:, 0])
print(f"가운데 (x, y): {np.round(가운데, 3)} (참값 [0.45 0.15])")
print(f"긴 변 방향(요): {요_도:.1f}도 (참값 30도, 180도 차이는 같은 방향)")
print(f"길이 {길이 * 100:.1f}cm, 폭 {폭 * 100:.1f}cm, 높이 {(윗면_높이 - 탁자) * 100:.1f}cm "
      f"(참값 {상자_반크기[0] * 200:.0f}, {상자_반크기[1] * 200:.0f}, {상자_반크기[2] * 200:.0f}cm)")
print(f"→ 집게 요 {요_도:.0f}도로 폭 {폭 * 100:.1f}cm를 집는다. TCP 높이 {탁자 + (윗면_높이 - 탁자) / 2:.3f}m")
