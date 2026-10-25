"""14장: 장면 모양에서 그린 점유 격자, 부풀림 비용 지도, 그 위의 A*."""
import heapq

import mujoco
import numpy as np
from scipy.ndimage import distance_transform_edt

해상도 = 0.05                 # m. 칸 하나의 한 변
지도_원점 = np.array([-0.3, -0.3])   # m. 격자 왼쪽 아래 모서리의 방 좌표
지도_크기 = (212, 172)        # 칸 수(x 방향, y 방향)
치명 = 254                    # 장애물이 있는 칸
내접 = 253                    # 로봇 중심이 오면 몸이 장애물에 닿는 칸


def 지도_그리기(모델: mujoco.MjModel) -> np.ndarray:
    """세상(body 0)에 붙은 group 0 상자·원기둥을 칸에 칠한 점유 격자(True = 찬칸)."""
    i, j = np.meshgrid(np.arange(지도_크기[0]), np.arange(지도_크기[1]), indexing="ij")
    cx, cy = 지도_원점[0] + (i + 0.5) * 해상도, 지도_원점[1] + (j + 0.5) * 해상도   # 칸 중심
    찬칸 = np.zeros(지도_크기, dtype=bool)
    for g in range(모델.ngeom):
        if 모델.geom_bodyid[g] != 0 or 모델.geom_group[g] != 0:
            continue
        (px, py, _), (sx, sy, _) = 모델.geom_pos[g], 모델.geom_size[g]
        if 모델.geom_type[g] == mujoco.mjtGeom.mjGEOM_BOX:
            찬칸 |= (abs(cx - px) <= sx) & (abs(cy - py) <= sy)
        elif 모델.geom_type[g] == mujoco.mjtGeom.mjGEOM_CYLINDER:
            찬칸 |= np.hypot(cx - px, cy - py) <= sx
    return 찬칸


def 비용_지도(찬칸: np.ndarray, 로봇_반지름: float = 0.2, 부풀림_반지름: float = 0.55,
          감쇠: float = 10.0) -> np.ndarray:
    """Nav2 부풀림 층과 같은 식: 장애물에서 멀어질수록 비용이 지수로 줄어든다(0~254)."""
    거리 = distance_transform_edt(~찬칸) * 해상도          # 칸마다 가장 가까운 찬칸까지(m)
    비용 = (내접 - 1) * np.exp(-감쇠 * (거리 - 로봇_반지름))
    비용[거리 > 부풀림_반지름] = 0
    비용[거리 <= 로봇_반지름] = 내접
    비용[찬칸] = 치명
    return 비용.astype(np.uint8)


def 칸으로(점) -> tuple[int, int]:
    i, j = np.floor((np.asarray(점) - 지도_원점) / 해상도).astype(int)
    return int(i), int(j)


def 점으로(칸) -> np.ndarray:
    return 지도_원점 + (np.asarray(칸) + 0.5) * 해상도


def a_star(비용: np.ndarray, 시작, 목표, 비용_무게: float = 3.0) -> np.ndarray | None:
    """13장의 A*를 비용 지도 위로: 한 칸 옮길 때 '거리 × (1 + 무게 × 비용/252)'를 낸다."""
    시작, 목표 = 칸으로(시작), 칸으로(목표)
    이웃 = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    g = {시작: 0.0}
    부모 = {}
    열린 = [(0.0, 시작)]
    while 열린:
        _, 지금 = heapq.heappop(열린)
        if 지금 == 목표:
            길 = [지금]
            while 길[-1] in 부모:
                길.append(부모[길[-1]])
            return np.array([점으로(칸) for 칸 in 길[::-1]])
        for di, dj in 이웃:
            다음 = (지금[0] + di, 지금[1] + dj)
            if not (0 <= 다음[0] < 지도_크기[0] and 0 <= 다음[1] < 지도_크기[1]) or 비용[다음] >= 내접:
                continue
            새_g = g[지금] + np.hypot(di, dj) * (1 + 비용_무게 * 비용[다음] / 252)
            if 새_g < g.get(다음, np.inf):
                g[다음], 부모[다음] = 새_g, 지금
                heapq.heappush(열린, (새_g + np.hypot(다음[0] - 목표[0], 다음[1] - 목표[1]), 다음))
    return None


def 장애물까지(찬칸: np.ndarray, 점들: np.ndarray) -> np.ndarray:
    """점들(N×2)에서 가장 가까운 찬칸 가장자리까지의 거리(m)."""
    거리표 = distance_transform_edt(~찬칸) * 해상도
    i, j = np.clip(np.floor((점들 - 지도_원점) / 해상도).astype(int), 0, np.array(지도_크기) - 1).T
    return 거리표[i, j] - 해상도 / 2
