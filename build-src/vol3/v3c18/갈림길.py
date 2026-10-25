"""18장: 가운데 장애물을 왼쪽으로도 오른쪽으로도 피해 가는 2차원 연습장."""
import numpy as np

출발, 도착 = np.array([0.0, 0.0]), np.array([0.0, 1.0])
장애물, 반지름 = np.array([0.0, 0.3]), 0.15
보폭 = 0.03                                   # 한 걸음에 움직이는 거리
최대_걸음 = 60


def 시연(개수: int, 씨앗: int = 0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """전문가는 에피소드마다 번갈아 왼쪽, 오른쪽으로 돌아간다. (상태, 행동, 에피소드 번호)."""
    생성기 = np.random.default_rng(씨앗)
    상태들, 행동들, 번호들 = [], [], []
    for i in range(개수):
        방향 = -1.0 if i % 2 == 0 else 1.0              # -1 왼쪽, +1 오른쪽
        경유 = np.array([방향 * 0.35, 장애물[1]])        # 장애물 옆을 지나는 점
        p = 출발 + 생성기.normal(0, 0.02, 2)              # 출발점은 시연마다 조금씩 다르다
        for _ in range(최대_걸음):
            목표 = 경유 if p[1] < 경유[1] - 0.05 else 도착
            a = 목표 - p
            a = a / max(np.linalg.norm(a), 1e-9) * 보폭
            상태들.append(p.copy())
            행동들.append(a)
            번호들.append(i)
            p = p + a
            if np.linalg.norm(p - 도착) < 보폭:
                break
    return np.array(상태들), np.array(행동들), np.array(번호들)


def 굴리기(정책, 개수: int) -> tuple[np.ndarray, np.ndarray]:
    """정책(상태 배치 → 행동 배치)으로 여러 에피소드를 한꺼번에. 모두 정확히 출발점에서. (궤적, 성공 여부)."""
    p = np.tile(출발, (개수, 1))
    궤적, 부딪힘, 도착함 = [p.copy()], np.zeros(개수, bool), np.zeros(개수, bool)
    for _ in range(최대_걸음):
        a = 정책(p)
        a = a / np.maximum(np.linalg.norm(a, axis=1, keepdims=True), 1e-9) * 보폭   # 보폭은 같게, 방향만 배운다
        p = np.where(도착함[:, None], p, p + a)                                   # 도착했으면 멈춘다
        부딪힘 |= np.linalg.norm(p - 장애물, axis=1) < 반지름
        도착함 |= np.linalg.norm(p - 도착, axis=1) < 0.05
        궤적.append(p.copy())
    return np.stack(궤적, axis=1), 도착함 & ~부딪힘
