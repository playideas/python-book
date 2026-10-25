import mujoco
import numpy as np

from 비전장면 import 장면_xml, 찍기

모델 = mujoco.MjModel.from_xml_string(장면_xml())
데이터 = mujoco.MjData(모델)
컬러, 깊이 = 찍기(모델, 데이터, "머리")
R, G, B = (컬러[..., i].astype(int) for i in range(3))
빨강 = (R > 100) & (G < 60) & (B < 60)
가운데_행, 가운데_열 = np.round(np.argwhere(빨강).mean(axis=0)).astype(int)
참_깊이 = np.median(깊이[빨강])


def 깊이_카메라(깊이: np.ndarray, 생성기: np.random.Generator) -> np.ndarray:
    """예제용 깊이 카메라 흉내: 거리 제곱에 비례하는 잡음 + 5% 픽셀은 값을 못 얻어 0."""
    잰 = 깊이 + 생성기.normal(0, 0.01 * 깊이**2)
    잰[생성기.random(깊이.shape) < 0.05] = 0.0
    return 잰


생성기 = np.random.default_rng(0)
결과 = {"가운데 픽셀 하나": [], "컵 픽셀 평균": [], "컵 픽셀 중앙값": [], "0을 뺀 중앙값": []}
for _ in range(200):
    잰 = 깊이_카메라(깊이, 생성기)
    컵 = 잰[빨강]
    결과["가운데 픽셀 하나"].append(잰[가운데_행, 가운데_열])
    결과["컵 픽셀 평균"].append(컵.mean())
    결과["컵 픽셀 중앙값"].append(np.median(컵))
    결과["0을 뺀 중앙값"].append(np.median(컵[컵 > 0]))

print(f"컵 픽셀 {빨강.sum()}개, 잡음 없는 중앙값 {참_깊이:.4f}m")
for 이름, 값들 in 결과.items():
    값들 = np.array(값들)
    print(f"{이름:9s}: 치우침 {(값들.mean() - 참_깊이) * 1000:+7.2f}mm, 흔들림(표준편차) {값들.std() * 1000:6.2f}mm")
