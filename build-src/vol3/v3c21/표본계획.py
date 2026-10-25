"""13장: 표본 기반 계획(PRM, RRT, RRT*)과 지름길 다듬기. 관절 공간의 점은 각도 배열(rad)."""
import heapq

import numpy as np


def 경로_길이(경로: np.ndarray) -> float:
    return float(np.linalg.norm(np.diff(경로, axis=0), axis=1).sum())


def 거슬러_잇기(점들, 부모, 끝: int) -> np.ndarray:
    """끝 점에서 부모를 따라 거슬러 올라가 시작부터의 경로로 만든다."""
    순서 = [끝]
    while 부모[순서[-1]] is not None:
        순서.append(부모[순서[-1]])
    return np.array([점들[i] for i in 순서[::-1]])


def PRM(시작, 목표, 충돌, 선분_충돌, 하한, 상한, 생성기, 표본_수: int = 300, 이웃_수: int = 10):
    """길 지도: 빈 곳에 점을 뿌리고, 가까운 점끼리 부딪히지 않으면 잇고, 그 위에서 다익스트라.
    0번이 시작, 1번이 목표. (경로, 점들, 간선 목록)을 돌려준다."""
    점들 = [np.asarray(시작, float), np.asarray(목표, float)]
    while len(점들) < 표본_수 + 2:
        q = 생성기.uniform(하한, 상한)
        if not 충돌(q):
            점들.append(q)
    점들 = np.array(점들)
    간선 = {i: [] for i in range(len(점들))}
    for i, q in enumerate(점들):
        거리 = np.linalg.norm(점들 - q, axis=1)
        for j in np.argsort(거리)[1:이웃_수 + 1]:
            if i < j and not 선분_충돌(q, 점들[j]):
                간선[i].append((int(j), 거리[j]))
                간선[int(j)].append((i, 거리[j]))
    비용, 부모, 더미 = {0: 0.0}, {0: None}, [(0.0, 0)]
    while 더미:
        d, i = heapq.heappop(더미)
        if i == 1:
            break
        for j, 길이 in 간선[i]:
            if d + 길이 < 비용.get(j, np.inf):
                비용[j], 부모[j] = d + 길이, i
                heapq.heappush(더미, (d + 길이, j))
    경로 = 거슬러_잇기(점들, 부모, 1) if 1 in 부모 else None
    return 경로, 점들, 간선


def RRT(시작, 목표, 선분_충돌, 하한, 상한, 생성기, 걸음: float = 0.2, 목표_쪽: float = 0.1,
        최대_반복: int = 5000, 별: bool = False, 반경: float = 0.5):
    """빨리 뻗는 무작위 나무. 별=True면 RRT*: 끝까지 돌며 부모를 고르고 이웃을 다시 잇는다.
    (경로 또는 None, 나무의 점들, 부모 번호들, 반복 수 또는 RRT*의 반복마다 가장 좋은 길이)."""
    목표 = np.asarray(목표, float)
    점들, 부모, 비용 = [np.asarray(시작, float)], [None], [0.0]
    목표_번호들, 기록 = [], []
    for 반복 in range(1, 최대_반복 + 1):
        # 가끔(목표_쪽 비율)은 목표 자체를 뽑아 나무를 목표 쪽으로 끌어당긴다
        표본 = 목표 if 생성기.random() < 목표_쪽 else 생성기.uniform(하한, 상한)
        배열 = np.array(점들)
        거리 = np.linalg.norm(배열 - 표본, axis=1)
        i = int(np.argmin(거리))                                   # 표본에서 가장 가까운 나무 점
        새점 = 표본 if 거리[i] <= 걸음 else 배열[i] + (표본 - 배열[i]) / 거리[i] * 걸음
        if not 선분_충돌(배열[i], 새점):
            새_거리 = np.linalg.norm(배열 - 새점, axis=1)
            이웃 = np.flatnonzero(새_거리 <= 반경) if 별 else []
            # RRT*: 이웃 중 '그 점까지 비용 + 새점까지 거리'가 가장 작은 곳을 부모로
            i = min((j for j in 이웃 if not 선분_충돌(배열[j], 새점)),
                    key=lambda j: 비용[j] + 새_거리[j], default=i)
            점들.append(새점)
            부모.append(int(i))
            비용.append(비용[i] + 새_거리[i])
            새번호 = len(점들) - 1
            for j in 이웃:          # 다시 잇기: 새점을 거쳐 가는 편이 싼 이웃은 부모를 바꾼다
                줄어듦 = 비용[j] - (비용[새번호] + 새_거리[j])
                if 줄어듦 > 1e-12 and not 선분_충돌(새점, 배열[j]):
                    부모[j] = 새번호
                    for k in 가지(부모, int(j)):                     # 그 아래 가지 전체가 싸진다
                        비용[k] -= 줄어듦
            if 별 and np.allclose(새점, 목표):
                목표_번호들.append(새번호)
            elif not 별 and np.linalg.norm(새점 - 목표) <= 걸음 and not 선분_충돌(새점, 목표):
                점들.append(목표)
                부모.append(새번호)
                return 거슬러_잇기(점들, 부모, len(점들) - 1), np.array(점들), 부모, 반복
        기록.append(min((비용[k] for k in 목표_번호들), default=np.inf))
    if not 목표_번호들:
        return None, np.array(점들), 부모, 최대_반복
    가장 = min(목표_번호들, key=lambda k: 비용[k])
    return 거슬러_잇기(점들, 부모, 가장), np.array(점들), 부모, 기록


def 가지(부모: list, 뿌리: int) -> list[int]:
    """뿌리와 그 아래 모든 점의 번호."""
    결과 = [뿌리]
    for k in 결과:
        결과.extend(i for i, p in enumerate(부모) if p == k)
    return 결과


def 지름길(경로: np.ndarray, 선분_충돌, 생성기, 시도: int = 200) -> np.ndarray:
    """경로 위 두 점을 무작위로 골라, 그 사이를 곧게 이어도 안 부딪히면 가운데를 잘라 낸다."""
    경로 = np.array(경로, dtype=float)
    for _ in range(시도):
        i, j = sorted(생성기.choice(len(경로), size=2, replace=False))
        if j - i >= 2 and not 선분_충돌(경로[i], 경로[j]):
            경로 = np.concatenate([경로[:i + 1], 경로[j:]])
    return 경로
