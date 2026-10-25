import matplotlib.pyplot as plt
import mujoco
import numpy as np
from scipy.spatial.transform import Rotation

from 비전장면 import K_만들기, R_로봇_머리, 머리_fovy, 머리_위치_로봇, 물체들, 변환, 장면_xml, 찍기, 축_글자
from 위치추정 import 물체_위치_추정
from 회전도구 import Rx, Rz

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

T_손_카메라 = 변환(Rz(90) @ Rx(-15), [0.05, 0.0, -0.02])        # 9.7절에서 보정한 손목 카메라 설치
T_로봇_손 = 변환(Rx(180) @ Rz(-90), [0.47, 0.0, 0.55])           # 순기구학이 알려 준 손 포즈: 탁자 위에서 아래를 본다
T_세계_로봇 = 변환(np.eye(3), [0, 0, 0.75])
T_세계_손 = T_세계_로봇 @ T_로봇_손
손 = (f'<body name="손" pos="{" ".join(map(str, T_세계_손[:3, 3]))}" '
     f'quat="{" ".join(map(str, Rotation.from_matrix(T_세계_손[:3, :3]).as_quat(scalar_first=True)))}">'
     f'<camera name="손목" pos="0.05 0 -0.02" xyaxes="{축_글자(T_손_카메라[:3, :3])}" fovy="60"/></body>')
모델 = mujoco.MjModel.from_xml_string(장면_xml(손))
데이터 = mujoco.MjData(모델)
생성기 = np.random.default_rng(0)
정답 = {이름: np.array(p) - [0, 0, 0.75] for 이름, (p, _, _) in 물체들.items()}   # 로봇 기준 정답

카메라들 = {"머리": (변환(R_로봇_머리, 머리_위치_로봇), K_만들기(머리_fovy)),
           "손목": (T_로봇_손 @ T_손_카메라, K_만들기(60))}
추정들, 사진들 = {}, {}
for 카메라, (T_로봇_카메라, K) in 카메라들.items():
    컬러, 깊이 = 찍기(모델, 데이터, 카메라)
    깊이 = 깊이 + 생성기.normal(0, 0.01 * 깊이**2)                    # 9.4절의 깊이 잡음 흉내
    깊이[생성기.random(깊이.shape) < 0.05] = 0.0
    추정들[카메라] = 물체_위치_추정(컬러, 깊이, K, T_로봇_카메라)
    사진들[카메라] = 컬러

print("물체 |        정답(로봇 기준, m) | 머리 오차 | 손목 오차 | 둘의 평균 오차")
for 이름, 참 in 정답.items():
    오차 = {k: np.linalg.norm(추정들[k][이름] - 참) * 100 for k in 추정들 if 이름 in 추정들[k]}
    평균 = np.mean([추정들[k][이름] for k in 추정들 if 이름 in 추정들[k]], axis=0)
    print(f"{이름} | {np.round(참, 3)} | " + " | ".join(f"{오차.get(k, np.nan):6.2f}cm" for k in 카메라들)
          + f" | {np.linalg.norm(평균 - 참) * 100:6.2f}cm")

그림, 칸들 = plt.subplots(1, 3, figsize=(11, 3.3), gridspec_kw={"width_ratios": [1.33, 1.33, 1]})
for 칸, 카메라 in zip(칸들, 카메라들):
    칸.imshow(사진들[카메라])
    칸.set_title(f"{카메라} 카메라", fontsize=10)
    칸.axis("off")
색 = {"빨강": "red", "초록": "green", "파랑": "blue", "노랑": "goldenrod"}
for 이름, 참 in 정답.items():
    칸들[2].scatter(참[1], 참[0], s=160, facecolors="none", edgecolors=색[이름])
    for 카메라, 모양 in [("머리", "x"), ("손목", "+")]:
        칸들[2].scatter(추정들[카메라][이름][1], 추정들[카메라][이름][0], marker=모양, color=색[이름])
칸들[2].set_xlabel("y (m, 로봇 왼쪽이 +)")
칸들[2].set_ylabel("x (m, 로봇 앞)")
칸들[2].invert_xaxis()                                            # 로봇 뒤에서 내려다본 방향으로
칸들[2].set_aspect("equal")
칸들[2].set_title("위에서 본 위치: ○ 정답 × 머리 + 손목", fontsize=9)
그림.tight_layout()
그림.subplots_adjust(top=0.9)
그림.savefig("practice.png", dpi=200)
print("저장: practice.png")
