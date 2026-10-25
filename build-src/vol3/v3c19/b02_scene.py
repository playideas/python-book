import mujoco
from PIL import Image

from 지시장면 import 그릇_중심, 물체들, 장면_xml, 찍기

모델 = mujoco.MjModel.from_xml_string(장면_xml())
데이터 = mujoco.MjData(모델)
컬러, 깊이 = 찍기(모델, 데이터)
Image.fromarray(컬러).save("scene.png")
for 이름, (모양, 반크기, _, 위치, 요) in 물체들.items():
    print(f"{이름}: {모양:8s} 위치 {위치}, 요 {요:3d}도, 크기 {[round(2 * 값 * 100, 1) for 값 in 반크기]}cm")
print(f"파란 그릇: 위치 {tuple(그릇_중심.tolist())}, 지름 16cm, 벽 높이 4cm")
print("사진", 컬러.shape, "깊이", 깊이.shape, f"깊이 범위 {깊이.min():.2f}~{깊이.max():.2f}m")
print("저장: scene.png")
