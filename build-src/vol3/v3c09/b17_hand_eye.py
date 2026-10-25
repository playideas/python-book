import mujoco
import numpy as np
from scipy.spatial.transform import Rotation

from 비전장면 import K_만들기, 바라보기, 변환, 장면_xml, 찍기, 축_글자
from 손눈 import 손눈_보정
from 표식 import 자세_차이, 표식_자세, 표식_조각
from 회전도구 import Rx, Rz, 깔끔

# 진짜 설치 값(로봇은 모른다): 손끝에서 5cm 옆, 2cm 뒤, 90도 돌리고 15도 기울여 달았다
T_손_카메라_참 = 변환(Rz(90) @ Rx(-15), [0.05, 0.0, -0.02])
표식_위치 = [0.7, -0.3, 0.751]
자산, 몸체, 파일 = 표식_조각(표식_위치, 요_도=10)
손 = (f'<body name="손" mocap="true"><geom type="box" size="0.02 0.02 0.04" pos="-0.02 0 -0.06" rgba="0.3 0.3 0.3 1"/>'
     f'<camera name="손목" pos="{" ".join(map(str, T_손_카메라_참[:3, 3]))}" '
     f'xyaxes="{축_글자(T_손_카메라_참[:3, :3])}" fovy="60"/></body>')
모델 = mujoco.MjModel.from_xml_string(장면_xml(몸체 + 손, 자산), assets=파일)
데이터 = mujoco.MjData(모델)
K = K_만들기(60)

생성기 = np.random.default_rng(0)
손_자세들, 표식_자세들 = [], []
for _ in range(12):
    # 표식이 보이도록 손을 이리저리 옮긴다. 로봇은 이 값(T_세계_손)을 순기구학으로 안다
    눈_위치 = np.array(표식_위치) + [*생성기.uniform(-0.15, 0.15, 2), 생성기.uniform(0.25, 0.4)]
    R_눈 = 바라보기(눈_위치, np.array(표식_위치) + [*생성기.uniform(-0.04, 0.04, 2), 0]) @ Rz(생성기.uniform(-60, 60))
    T_세계_손 = 변환(R_눈, 눈_위치) @ np.linalg.inv(T_손_카메라_참)
    데이터.mocap_pos[1] = T_세계_손[:3, 3]                     # 0번 mocap은 표식, 1번이 손
    데이터.mocap_quat[1] = Rotation.from_matrix(T_세계_손[:3, :3]).as_quat(scalar_first=True)
    컬러, _ = 찍기(모델, 데이터, "손목")
    T_카메라_표식 = 표식_자세(컬러, K)
    if T_카메라_표식 is not None:
        손_자세들.append(T_세계_손)
        표식_자세들.append(T_카메라_표식)

T_손_카메라 = 손눈_보정(손_자세들, 표식_자세들)
print(f"쓸 수 있는 자세 {len(손_자세들)}개")
print("추정한 카메라 위치(손 기준):", 깔끔(T_손_카메라[:3, 3]), "/ 진짜:", 깔끔(T_손_카메라_참[:3, 3]))
위치_오차, 각도_오차 = 자세_차이(T_손_카메라, T_손_카메라_참)
print(f"오차: 위치 {위치_오차:.2f}cm, 자세 {각도_오차:.2f}도")

# 정답 없이 하는 확인: 자세마다 '세계 기준 표식 위치'를 계산해 서로 얼마나 모이는지 본다
표식_세계 = np.array([(T손 @ T_손_카메라 @ T표)[:3, 3] for T손, T표 in zip(손_자세들, 표식_자세들)])
print("자세마다 계산한 표식 위치의 흩어짐(표준편차, mm):", 깔끔(표식_세계.std(axis=0) * 1000, 1))

qx, qy, qz, qw = Rotation.from_matrix(T_손_카메라[:3, :3]).as_quat()
x, y, z = T_손_카메라[:3, 3]
print("6장의 정적 변환으로 등록하려면:")
print(f"ros2 run tf2_ros static_transform_publisher --x {x:.4f} --y {y:.4f} --z {z:.4f} "
      f"--qx {qx:.4f} --qy {qy:.4f} --qz {qz:.4f} --qw {qw:.4f} --frame-id link6 --child-frame-id camera")
