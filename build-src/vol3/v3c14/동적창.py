"""14장: 동적 창 방식(DWA). 지금 낼 수 있는 (v, ω)들을 짧게 굴려 보고 가장 좋은 것을 고른다."""
import numpy as np

최고_v, 최저_v = 0.5, 0.0          # m/s. 후진은 복구 행동에서만
최고_ω = 1.5                       # rad/s
가속_v, 가속_ω = 1.0, 3.0          # m/s², rad/s²
주기 = 0.1                         # s. 제어 주기
내다볼_초, 굴림_간격 = 1.5, 0.1    # s
몸_반지름 = 0.2                    # m
무게 = {"목표": 1.0, "여유": 0.6, "속도": 0.4}


def 후보_굴리기(포즈, v들: np.ndarray, ω들: np.ndarray) -> np.ndarray:
    """후보마다 내다볼_초 동안 굴린 궤적. 모양 (후보 수, 걸음 수, 3)."""
    걸음 = round(내다볼_초 / 굴림_간격)
    궤적 = np.zeros((len(v들), 걸음, 3))
    x, y, θ = (np.full(len(v들), 값, dtype=float) for 값 in 포즈)
    for k in range(걸음):
        θ = θ + ω들 * 굴림_간격
        x = x + v들 * np.cos(θ) * 굴림_간격
        y = y + v들 * np.sin(θ) * 굴림_간격
        궤적[:, k] = np.column_stack([x, y, θ])
    return 궤적


def dwa(포즈, 지금_v: float, 지금_ω: float, 목표점, 장애물점: np.ndarray) -> dict:
    """가장 점수가 높은 (v, ω)와, 그림을 그릴 수 있게 후보 전부를 돌려준다."""
    v_범위 = np.linspace(max(최저_v, 지금_v - 가속_v * 주기), min(최고_v, 지금_v + 가속_v * 주기), 7)
    ω_범위 = np.linspace(max(-최고_ω, 지금_ω - 가속_ω * 주기), min(최고_ω, 지금_ω + 가속_ω * 주기), 15)
    v들, ω들 = (a.ravel() for a in np.meshgrid(v_범위, ω_범위))
    궤적 = 후보_굴리기(포즈, v들, ω들)
    가까운 = 장애물점[np.linalg.norm(장애물점 - 포즈[:2], axis=1) < 3.0] if len(장애물점) else 장애물점
    if len(가까운):
        사이 = np.linalg.norm(궤적[:, :, None, :2] - 가까운[None, None], axis=3)
        여유 = 사이.min(axis=(1, 2)) - 몸_반지름
    else:
        여유 = np.full(len(v들), 3.0)
    # 부딪히거나, 지금 브레이크를 잡아도 장애물 앞에서 못 서는 후보는 버린다
    가능 = (여유 > 0) & (v들 <= np.sqrt(2 * 가속_v * np.maximum(여유, 0)))
    끝_거리 = np.linalg.norm(궤적[:, -1, :2] - 목표점, axis=1)
    점수 = -무게["목표"] * 끝_거리 + 무게["여유"] * np.minimum(여유, 0.5) + 무게["속도"] * v들
    점수[~가능] = -np.inf
    최선 = int(np.argmax(점수))
    return {"v": float(v들[최선]) if 가능.any() else 0.0, "ω": float(ω들[최선]) if 가능.any() else 0.0,
            "막힘": not 가능.any(), "궤적": 궤적, "가능": 가능, "최선": 최선}
