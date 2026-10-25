import mujoco
import numpy as np
from PIL import Image

from 책상장면 import 대기_자세, 무작위_배치, 상자들, 연필꽂이, 장면_xml, 찍기

물건들 = 무작위_배치(np.random.default_rng(0), {"빨강": 2, "초록": 2, "파랑": 1})
모델 = mujoco.MjModel.from_xml_string(장면_xml(물건들))
데이터 = mujoco.MjData(모델)
데이터.qpos[:6] = 데이터.ctrl[:6] = 대기_자세              # 팔은 뒤로 돌려 둔 대기 자세에서 시작
for _ in range(500):                                        # 1초 동안 물건이 책상에 자리 잡게 둔다
    mujoco.mj_step(모델, 데이터)
컬러, 깊이 = 찍기(모델, 데이터)
Image.fromarray(컬러).save("desk_scene.png")
for 물건 in 물건들:
    print(f"{물건['이름']}: ({물건['위치'][0]:.3f}, {물건['위치'][1]:.3f}), 요 {물건['요']:6.1f}도")
print("정리 상자:", {종류: tuple(곳.round(3).tolist()) for 종류, 곳 in 상자들.items()},
      f"/ 연필꽂이: {tuple(연필꽂이[0].tolist())}, 높이 {연필꽂이[2]}m")
print(f"자유도: 관절 {모델.njnt}개, qpos {모델.nq}개 / 액추에이터 {모델.nu}개")
print("저장: desk_scene.png")
