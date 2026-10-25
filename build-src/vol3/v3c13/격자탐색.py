"""13장: 점유 격자 위의 BFS, 다익스트라, A*. 칸은 (i, j), 통과[i, j]가 True면 갈 수 있는 칸."""
import heapq

import numpy as np

# 여덟 방향 이웃: (칸 이동 i, 칸 이동 j, 비용). 대각선은 칸 한 변의 √2배
이웃들 = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
        (1, 1, 2**0.5), (1, -1, 2**0.5), (-1, 1, 2**0.5), (-1, -1, 2**0.5)]


def 옥타일(a, b) -> float:
    """장애물이 없을 때 여덟 방향으로 가는 가장 짧은 칸 거리: 대각선으로 갈 만큼 가고 나머지는 곧게."""
    di, dj = abs(a[0] - b[0]), abs(a[1] - b[1])
    return max(di, dj) + (2**0.5 - 1) * min(di, dj)


def 맨해튼(a, b) -> float:
    """가로·세로로만 가는 거리. 대각선을 쓰는 지도에서는 실제보다 길게 어림한다."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def 갈_수_있는_이웃(통과: np.ndarray, 칸):
    """지도 안이고 막히지 않은 이웃. 대각선은 양옆 두 칸이 모두 비어야 간다(모서리 긁기 금지)."""
    i, j = 칸
    for di, dj, 비용 in 이웃들:
        a, b = i + di, j + dj
        if 0 <= a < 통과.shape[0] and 0 <= b < 통과.shape[1] and 통과[a, b] \
                and 통과[i + di, j] and 통과[i, j + dj]:
            yield (a, b), 비용


def 탐색(통과: np.ndarray, 시작, 목표, 방법: str = "A*", 휴리스틱=옥타일, 가중치: float = 1.0):
    """(경로 칸 목록, 펼친 칸 표시 배열). 목표가 None이면 끝까지 펼쳐 (비용 배열, 펼친 칸)을 돌려준다.
    BFS는 모든 걸음을 1로 센다. 다익스트라는 진짜 비용, A*는 비용 + 가중치 × 휴리스틱 순서로 꺼낸다."""
    비용 = np.full(통과.shape, np.inf)          # 시작에서 그 칸까지 지금까지 찾은 가장 싼 비용 g
    비용[시작] = 0.0
    펼침 = np.zeros(통과.shape, dtype=bool)
    부모, 더미 = {시작: None}, [(0.0, 시작)]
    while 더미:
        _, 칸 = heapq.heappop(더미)
        if 펼침[칸]:
            continue                            # 더 싼 길로 이미 펼친 칸
        펼침[칸] = True
        if 칸 == 목표:
            경로 = [목표]
            while 부모[경로[-1]] is not None:
                경로.append(부모[경로[-1]])
            return 경로[::-1], 펼침
        for 다음, 한걸음 in 갈_수_있는_이웃(통과, 칸):
            새_비용 = 비용[칸] + (1.0 if 방법 == "BFS" else 한걸음)
            if 새_비용 < 비용[다음]:
                비용[다음], 부모[다음] = 새_비용, 칸
                h = 휴리스틱(다음, 목표) if 방법 == "A*" else 0.0
                heapq.heappush(더미, (새_비용 + 가중치 * h, 다음))
    return (비용, 펼침) if 목표 is None else ([], 펼침)


def 경로_길이(경로, 해상도: float) -> float:
    """칸 경로의 길이(m)."""
    return float(np.linalg.norm(np.diff(np.array(경로, dtype=float), axis=0), axis=1).sum() * 해상도)
