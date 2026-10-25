import numpy as np

from 조명장면 import IoU, 빨강_마스크, 조명카메라

카메라 = 조명카메라()
생성기 = np.random.default_rng(0)
s_후보, v_후보 = [40, 80, 120, 160], [5, 10, 20, 40, 60]

# 고를 때 쓰는 사진들: 9장 장면 그대로 한 장, 그리고 조명을 무작위로 흔든 40장
그대로 = [카메라.찍기()]
흔든 = [카메라.찍기(밝기=생성기.uniform(0.1, 1.3), 색조=생성기.uniform(0.4, 1.0, 3), 잡음=생성기.uniform(0, 6),
                  컵색_흔들기=0.1, 생성기=생성기) for _ in range(40)]
# 시험하는 사진들: '현실 역할' 방. 어둡고 누런 전등, 카메라 잡음. 고를 때는 쓰지 않는다
현실 = [카메라.찍기(밝기=생성기.uniform(0.15, 0.35), 색조=(1.0, 0.75, 0.45), 잡음=4, 생성기=생성기) for _ in range(10)]


def 평균_IoU(사진들: list, s: int, v: int) -> float:
    return float(np.mean([IoU(빨강_마스크(컬러, s, v), 정답) for 컬러, 정답 in 사진들]))


print("밝기 문턱(채도 120) | 9장 장면 그대로 | 무작위화 40장 | 현실 역할 방")
for v in v_후보:
    print(f"{v:18d} | {평균_IoU(그대로, 120, v):15.2f} | {평균_IoU(흔든, 120, v):13.2f} | {평균_IoU(현실, 120, v):11.2f}")

표 = np.array([[평균_IoU(흔든, s, v) for v in v_후보] for s in s_후보])
i, j = np.unravel_index(np.argmax(표), 표.shape)
print(f"무작위화 40장에서 가장 좋은 문턱: 채도 {s_후보[i]}, 밝기 {v_후보[j]} (IoU {표[i, j]:.2f})"
      f" → 현실 역할 방 IoU {평균_IoU(현실, s_후보[i], v_후보[j]):.2f}")
