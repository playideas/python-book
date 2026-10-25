import mujoco
import numpy as np

from 비전장면 import K_만들기, T_세계_카메라, 높이, 너비, 머리_fovy, 장면_xml

# 탁자 위에 작은 구슬 다섯 개를 놓는다. 위치(세계 기준)를 정확히 안다
구슬_세계 = np.array([[0.35, 0.20, 0.76], [0.50, 0.0, 0.76], [0.70, -0.30, 0.76],
                     [0.80, 0.35, 0.76], [0.42, -0.22, 0.76]])
추가 = "\n".join(f'<geom name="구슬{i}" type="sphere" size="0.006" pos="{" ".join(map(str, p))}" rgba="1 1 1 1"/>'
                for i, p in enumerate(구슬_세계))
모델 = mujoco.MjModel.from_xml_string(장면_xml(추가))
데이터 = mujoco.MjData(모델)
mujoco.mj_forward(모델, 데이터)
with mujoco.Renderer(모델, 높이, 너비) as 렌더러:
    렌더러.enable_segmentation_rendering()       # 픽셀마다 '어느 geom인가'를 찍는다
    렌더러.update_scene(데이터, camera="머리")
    분할 = 렌더러.render()[..., 0]

K = K_만들기(머리_fovy)
print("K =\n", np.round(K, 1))
T_카메라_세계 = np.linalg.inv(T_세계_카메라(데이터, "머리"))
for i, p in enumerate(구슬_세계):
    X, Y, Z = (T_카메라_세계 @ [*p, 1.0])[:3]          # 세계 → 카메라 광학 좌표
    u, v, _ = K @ [X / Z, Y / Z, 1.0]                   # 투영
    행들, 열들 = np.nonzero(분할 == 모델.geom(f"구슬{i}").id)
    print(f"구슬{i}: 깊이 {Z:.3f}m, 계산 ({u:6.1f}, {v:6.1f}), 사진 속 ({열들.mean():6.1f}, {행들.mean():6.1f})")
