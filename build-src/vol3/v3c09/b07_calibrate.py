import cv2
import numpy as np

from 체커보드 import K_참, 보드_사진들, 왜곡_참, 칸_수, 칸_크기

안쪽 = (칸_수[0] - 1, 칸_수[1] - 1)                          # 안쪽 꼭짓점 8×6
보드_점 = np.zeros((안쪽[0] * 안쪽[1], 3), np.float32)      # 보드 기준 꼭짓점 위치(z=0 평면)
보드_점[:, :2] = np.mgrid[0:안쪽[0], 0:안쪽[1]].T.reshape(-1, 2) * 칸_크기
멈춤 = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


def 꼭짓점_모으기(사진들: list[np.ndarray]) -> list[np.ndarray]:
    """사진마다 안쪽 꼭짓점을 찾아 소수점 픽셀까지 다듬는다. 못 찾은 사진은 버린다."""
    결과 = []
    for 사진 in 사진들:
        회색 = cv2.cvtColor(사진, cv2.COLOR_RGB2GRAY)
        찾음, 꼭짓점 = cv2.findChessboardCorners(회색, 안쪽)
        if 찾음:
            결과.append(cv2.cornerSubPix(회색, 꼭짓점, (5, 5), (-1, -1), 멈춤))
    return 결과


# 렌즈가 진짜로 하는 일: 각 픽셀로 들어오는 빛의 방향(사진 전체를 20픽셀 간격으로)
v, u = np.mgrid[0:480:20, 0:640:20]
격자 = np.stack([u.ravel(), v.ravel()], axis=1).astype(np.float64)[:, None, :]
광선 = np.concatenate([cv2.undistortPoints(격자, K_참, 왜곡_참).reshape(-1, 2), np.ones((len(격자), 1))], axis=1)

print("                       fx     fy     cx     cy |    k1     k2     k3 | 재투영  | 가장 큰 차이")
print("참값              " + "".join(f"{x:7.1f}" for x in K_참[[0, 1, 0, 1], [0, 1, 2, 2]]) + " |"
      + "".join(f"{x:7.3f}" for x in 왜곡_참[[0, 1, 4]]))
for 이름, 사진들 in [("가운데만", 보드_사진들(15, 퍼짐=0.2)), ("구석까지", 보드_사진들(30))]:
    픽셀점들 = 꼭짓점_모으기(사진들)
    for 모형, 설정 in [("모두", 0), ("k3=0", cv2.CALIB_FIX_K3)]:
        오차, K, 왜곡, _, _ = cv2.calibrateCamera([보드_점] * len(픽셀점들), 픽셀점들, (640, 480),
                                                None, None, flags=설정)
        # 진짜 방향에서 온 빛이 추정한 카메라 모형으로는 어디에 찍히나 → 실제 픽셀과의 차이
        다시_찍기, _ = cv2.projectPoints(광선, np.zeros(3), np.zeros(3), K, 왜곡)
        차이 = np.linalg.norm(다시_찍기 - 격자, axis=2).max()
        print(f"{이름} {len(픽셀점들):2d}장 {모형}" + "".join(f"{x:7.1f}" for x in K[[0, 1, 0, 1], [0, 1, 2, 2]])
              + " |" + "".join(f"{x:7.3f}" for x in 왜곡.ravel()[[0, 1, 4]]) + f" | {오차:.3f}px | {차이:6.2f}px")
