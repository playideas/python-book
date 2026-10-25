import matplotlib.pyplot as plt
import mujoco
import numpy as np

from 골격도구 import 골격_그리기
from 사람모델 import 키포인트_3d
from 사람장면 import 사람_xml
from 자세모델 import 모델_불러오기, 자세_찾기, 장치_고르기
from 카메라도구 import 바라보기, 카메라_만들기, 투영

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

도 = np.deg2rad
점들 = 키포인트_3d(오른팔_각=[도(120), 0, 도(-90), 도(60)], 왼팔_각=[도(10), 0, 0, 도(20)])
초점_px, 너비, 높이 = 600.0, 640, 480
시야각_도 = np.rad2deg(2 * np.arctan(높이 / 2 / 초점_px))     # MuJoCo는 세로 시야각(fovy)을 받는다

장치 = 장치_고르기()
모델 = 모델_불러오기(장치)
그림, 칸들 = plt.subplots(1, 3, figsize=(9, 2.6))
for 칸, (이름, 위치) in zip(칸들, {"정면": [3, 0, 1.2], "오른쪽 앞": [2.5, -1.5, 1.3],
                                   "왼쪽 앞": [2.2, 1.5, 1.0]}.items()):
    R_세계_카메라 = 바라보기(위치, [0, 0, 0.9])
    # MuJoCo 카메라는 x 오른쪽, y 위를 쓰므로 광학 좌표의 y(아래)를 뒤집어 넘긴다
    장면 = mujoco.MjModel.from_xml_string(사람_xml(점들, 위치, R_세계_카메라[:, 0], -R_세계_카메라[:, 1], 시야각_도))
    상태 = mujoco.MjData(장면)
    mujoco.mj_forward(장면, 상태)
    with mujoco.Renderer(장면, 높이, 너비) as 렌더러:
        렌더러.update_scene(상태, camera="cam")
        이미지 = 렌더러.render()
    결과 = 자세_찾기(모델, 이미지, 장치)
    최고 = 결과["점수"].max() if len(결과["점수"]) else 0.0
    print(f"{이름}: 사람 후보 {len(결과['점수'])}개, 가장 높은 사람 점수 {최고:.3f}")
    칸.imshow(이미지)
    골격_그리기(칸, 투영(카메라_만들기(위치, [0, 0, 0.9], 초점_px, 너비, 높이), 점들), 굵기=1.5)
    칸.set_title(이름)
    칸.axis("off")
그림.tight_layout()
그림.savefig("synth_person.png", dpi=200)
print("저장: synth_person.png")
