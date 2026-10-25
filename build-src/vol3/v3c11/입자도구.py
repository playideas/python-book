"""11장: 지도를 알 때 파티클 필터로 위치 찾기(MCL)."""
import numpy as np
from scipy.ndimage import distance_transform_edt

from 격자도구 import 지도_원점, 지도_크기, 해상도
from 포즈도구 import 각도_정리

측정_시그마 = 0.3        # m. 스캔 점이 지도의 벽에서 이만큼 벗어나는 것은 흔한 일로 본다
움직임_잡음 = (0.03, 0.02)   # 한 걸음마다 입자에 뿌리는 거리(m), 방향(rad) 잡음


def 벽까지_거리표(점유확률: np.ndarray) -> np.ndarray:
    """칸마다 가장 가까운 찬칸까지의 거리(m). 스캔 점이 벽에 얼마나 붙는지 빨리 보려고 미리 계산한다."""
    return distance_transform_edt(점유확률 < 0.65) * 해상도


def 입자_뿌리기(개수: int, 점유확률: np.ndarray, 생성기: np.random.Generator) -> np.ndarray:
    """확실한 빈칸 위에 고르게 입자 (x, y, 각)를 뿌린다. 위치를 전혀 모를 때."""
    빈칸 = np.argwhere(점유확률 < 0.2)
    고른 = 빈칸[생성기.integers(len(빈칸), size=개수)]
    xy = 지도_원점 + (고른 + 생성기.random((개수, 2))) * 해상도
    return np.column_stack([xy, 생성기.uniform(-np.pi, np.pi, 개수)])


def 입자_움직이기(입자들: np.ndarray, 증분, 생성기: np.random.Generator) -> np.ndarray:
    """바퀴 오도메트리 증분을 입자마다 자기 방향 기준으로 적용하고, 잡음을 뿌린다."""
    n = len(입자들)
    앞 = 증분[0] + 생성기.normal(0, 움직임_잡음[0], n)
    옆 = 증분[1] + 생성기.normal(0, 움직임_잡음[0], n)
    회전 = 증분[2] + 생성기.normal(0, 움직임_잡음[1], n)
    c, s = np.cos(입자들[:, 2]), np.sin(입자들[:, 2])
    return np.column_stack([입자들[:, 0] + c * 앞 - s * 옆,
                            입자들[:, 1] + s * 앞 + c * 옆,
                            각도_정리(입자들[:, 2] + 회전)])


def 입자_가중치(입자들: np.ndarray, 스캔: np.ndarray, 거리표: np.ndarray) -> np.ndarray:
    """입자마다 '이 자리에서 잰 스캔이라면 점들이 벽에 얼마나 붙는가'로 점수를 매긴다."""
    c, s = np.cos(입자들[:, 2])[:, None], np.sin(입자들[:, 2])[:, None]
    x = 입자들[:, 0:1] + c * 스캔[:, 0] - s * 스캔[:, 1]       # (입자 수, 점 수)
    y = 입자들[:, 1:2] + s * 스캔[:, 0] + c * 스캔[:, 1]
    i = np.floor((x - 지도_원점[0]) / 해상도).astype(int)
    j = np.floor((y - 지도_원점[1]) / 해상도).astype(int)
    안 = (i >= 0) & (i < 지도_크기[0]) & (j >= 0) & (j < 지도_크기[1])
    d = np.where(안, 거리표[np.clip(i, 0, 지도_크기[0] - 1), np.clip(j, 0, 지도_크기[1] - 1)], 1.0)
    로그_점수 = -0.5 * (np.minimum(d, 0.5) / 측정_시그마) ** 2      # 멀리 벗어난 점 하나가 전부를 망치지 않게
    로그_점수 = 로그_점수.sum(axis=1)
    w = np.exp(로그_점수 - 로그_점수.max())
    return w / w.sum()


def 다시_뽑기(입자들: np.ndarray, 가중치: np.ndarray, 생성기: np.random.Generator) -> np.ndarray:
    """가중치에 비례해 입자를 다시 뽑는다(계통 재표본: 같은 간격의 빗으로 한 번에)."""
    n = len(입자들)
    빗 = (생성기.random() + np.arange(n)) / n
    번호 = np.searchsorted(np.cumsum(가중치), 빗)
    return 입자들[np.minimum(번호, n - 1)].copy()
