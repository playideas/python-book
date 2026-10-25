"""13장: 경유점을 스플라인으로 잇고, 속도·가속도 한계를 지키는 사다리꼴 속도로 시간을 매긴다."""
import numpy as np
from scipy.interpolate import CubicSpline


def 사다리꼴(거리: float, v최대: float, a최대: float):
    """거리를 멈춤 → 가속 → 등속 → 감속 → 멈춤으로 간다. (걸리는 시간, 시각 → 간 거리 함수).
    거리가 짧아 v최대에 못 미치면 등속 구간 없이 삼각형이 된다."""
    가속_시간 = v최대 / a최대
    if 거리 < v최대 * 가속_시간:                   # 가속·감속만으로 거리를 다 쓴다(삼각형)
        가속_시간 = np.sqrt(거리 / a최대)
        v최대 = a최대 * 가속_시간
    등속_시간 = (거리 - v최대 * 가속_시간) / v최대
    총시간 = 2 * 가속_시간 + 등속_시간

    def 간_거리(t):
        t = np.clip(t, 0, 총시간)
        남은_t = 총시간 - t
        return np.where(t < 가속_시간, 0.5 * a최대 * t**2,
                        np.where(남은_t < 가속_시간, 거리 - 0.5 * a최대 * 남은_t**2,
                                 0.5 * a최대 * 가속_시간**2 + v최대 * (t - 가속_시간)))
    return 총시간, 간_거리


def 스플라인(경유점들: np.ndarray, 개수: int = 2000) -> np.ndarray:
    """경유점을 모두 지나는 매끄러운 곡선(3차 스플라인)을 개수만큼 촘촘히 찍는다.
    매개변수는 경유점 사이 거리를 쌓은 값이고, 양 끝에서는 기울기 0으로 시작하고 멈춘다."""
    누적 = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(경유점들, axis=0), axis=1))])
    곡선 = CubicSpline(누적, 경유점들, bc_type="clamped")
    return 곡선(np.linspace(0, 누적[-1], 개수))


def 안전한_스플라인(경유점들: np.ndarray, 부딪힘, 최대_횟수: int = 6) -> tuple[np.ndarray, int]:
    """스플라인이 장애물을 파고들면, 경유점 사이마다 가운데 점을 넣어 꺾은선에 더 붙게 한다.
    부딪힘(점들)은 점들 중 하나라도 부딪히면 True. (곡선, 가운데 점을 넣은 횟수)를 돌려준다."""
    for 횟수 in range(최대_횟수 + 1):
        곡선 = 스플라인(경유점들)
        if not 부딪힘(곡선):
            return 곡선, 횟수
        가운데 = (경유점들[:-1] + 경유점들[1:]) / 2
        끼움 = np.empty((len(경유점들) + len(가운데), 경유점들.shape[1]))
        끼움[0::2], 끼움[1::2] = 경유점들, 가운데
        경유점들 = 끼움
    raise RuntimeError("안전한 스플라인을 찾지 못했다. 꺾은선 그대로 쓰자")


def 멈추며_가는_궤적(경유점들: np.ndarray, v최대: float, a최대: float):
    """꺾은선의 구간마다 사다리꼴 하나씩: 경유점마다 멈췄다 간다. (걸리는 시간, 시각 → 자세 함수)."""
    구간들 = [(a, b, *사다리꼴(np.linalg.norm(b - a), v최대, a최대)) for a, b in zip(경유점들[:-1], 경유점들[1:])]
    시작_시각 = np.concatenate([[0], np.cumsum([구간[2] for 구간 in 구간들])])

    def 자세(t: float) -> np.ndarray:
        k = min(int(np.searchsorted(시작_시각, t, side="right")) - 1, len(구간들) - 1)
        a, b, _, 간_거리 = 구간들[max(k, 0)]
        비율 = 간_거리(t - 시작_시각[max(k, 0)]) / max(np.linalg.norm(b - a), 1e-12)
        return a + 비율 * (b - a)
    return float(시작_시각[-1]), 자세
