import mujoco
from PIL import Image

from 비전장면 import 장면_xml, 찍기

모델 = mujoco.MjModel.from_xml_string(장면_xml())
데이터 = mujoco.MjData(모델)
컬러, 깊이 = 찍기(모델, 데이터, "머리")

print("컬러 사진:", 컬러.shape, 컬러.dtype)
print("깊이 영상:", 깊이.shape, 깊이.dtype)
print("가운데 픽셀(행 240, 열 320) RGB:", 컬러[240, 320], "/ 깊이:", round(float(깊이[240, 320]), 3), "m")
Image.fromarray(컬러).save("head_view.png")
print("저장: head_view.png")
