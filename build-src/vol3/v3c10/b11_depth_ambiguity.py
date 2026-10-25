import numpy as np

from 골격도구 import 번호
from 사람모델 import 아래팔_길이, 위팔_길이, 키포인트_3d
from 카메라도구 import 카메라_만들기, 투영

도 = np.deg2rad
P = 카메라_만들기([3.0, 0.0, 1.3], [0, 0, 1.2])          # 정면 카메라 한 대
점들 = 키포인트_3d(오른팔_각=[도(120), 0, 도(-90), 도(60)])
어깨, 팔꿈치, 손목 = (점들[번호[이름]] for 이름 in ["오른어깨", "오른팔꿈치", "오른손목"])


def 광선(P: np.ndarray, 픽셀) -> tuple[np.ndarray, np.ndarray]:
    """픽셀 하나가 가리키는 3D 반직선: 카메라 중심과 단위 방향. P = [M | p] 에서 구한다."""
    M, p = P[:, :3], P[:, 3]
    방향 = np.linalg.solve(M, [픽셀[0], 픽셀[1], 1.0])
    return -np.linalg.solve(M, p), 방향 / np.linalg.norm(방향)


def 길이로_찾기(시작: np.ndarray, 중심: np.ndarray, 방향: np.ndarray, 길이: float) -> list[np.ndarray]:
    """광선 위에서 시작점과 거리가 '길이'인 점들. 이차방정식이라 답이 0~2개다."""
    b = 방향 @ (중심 - 시작)
    판별식 = b**2 - (np.sum((중심 - 시작) ** 2) - 길이**2)
    if 판별식 < 0:
        return []
    return [중심 + (-b + 부호 * np.sqrt(판별식)) * 방향 for 부호 in (-1, +1)]


# 1) 광선을 따라 앞뒤로 밀면 사진은 같다
중심, 방향 = 광선(P, 투영(P, 팔꿈치[None])[0])
밀린_팔꿈치 = 팔꿈치 + 0.3 * 방향                           # 카메라에서 30cm 더 멀리
print("팔꿈치 픽셀:", np.round(투영(P, 팔꿈치[None])[0], 2), "→ 30cm 밀어도", np.round(투영(P, 밀린_팔꿈치[None])[0], 2))
print(f"그때 위팔 길이: {np.linalg.norm(밀린_팔꿈치 - 어깨):.3f}m (진짜 {위팔_길이}m)")

# 2) 뼈 길이를 알면 후보가 둘로 줄어든다
후보들 = 길이로_찾기(어깨, 중심, 방향, 위팔_길이)
for k, 후보 in enumerate(후보들):
    _, 손목_방향 = 광선(P, 투영(P, 손목[None])[0])
    손목_후보들 = 길이로_찾기(후보, 중심, 손목_방향, 아래팔_길이)
    print(f"팔꿈치 후보 {k + 1}: {np.round(후보, 3) + 0.0}, 손목 후보 {len(손목_후보들)}개 →",
          ", ".join(str(np.round(w, 3) + 0.0) for w in 손목_후보들))
print("진짜 팔꿈치:", np.round(팔꿈치, 3) + 0.0, "/ 진짜 손목:", np.round(손목, 3) + 0.0)
