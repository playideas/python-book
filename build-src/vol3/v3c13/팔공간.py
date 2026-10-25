"""13장: 둥근 장애물이 있는 평면에서 3장의 2링크 팔이 부딪히는지 검사한다."""
import numpy as np

from 두링크 import 아래팔, 위팔

링크_반지름 = 0.02                            # m. 팔 막대의 두께(반지름)
장애물들 = np.array([[0.45, 0.30, 0.10],       # (x, y, 반지름) m
                    [-0.20, 0.45, 0.10],
                    [0.10, -0.45, 0.12]])
하한 = np.array([-np.pi, -np.pi])            # 관절 범위(rad): 어깨, 팔꿈치
상한 = np.array([np.pi, np.pi])


def 관절_점들(q: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """관절 각도들(…×2) → 팔꿈치, 손끝 위치(…×2). 여러 자세를 한꺼번에 계산할 수 있다."""
    q = np.asarray(q, dtype=float)
    팔꿈치 = 위팔 * np.stack([np.cos(q[..., 0]), np.sin(q[..., 0])], axis=-1)
    합 = q[..., 0] + q[..., 1]
    손끝 = 팔꿈치 + 아래팔 * np.stack([np.cos(합), np.sin(합)], axis=-1)
    return 팔꿈치, 손끝


def 선분_거리(a: np.ndarray, b: np.ndarray, 점: np.ndarray) -> np.ndarray:
    """선분 a-b와 점 사이의 가장 짧은 거리(…)."""
    ab, ap = b - a, 점 - a
    t = np.clip(np.sum(ap * ab, axis=-1) / np.maximum(np.sum(ab * ab, axis=-1), 1e-12), 0, 1)
    return np.linalg.norm(ap - t[..., None] * ab, axis=-1)


def 여유(q: np.ndarray) -> np.ndarray:
    """팔 표면과 가장 가까운 장애물 표면 사이의 거리(m). 0보다 작으면 부딪힌 것."""
    팔꿈치, 손끝 = 관절_점들(q)
    바닥 = np.zeros_like(팔꿈치)
    거리 = []
    for x, y, r in 장애물들:
        중심 = np.array([x, y])
        d = np.minimum(선분_거리(바닥, 팔꿈치, 중심), 선분_거리(팔꿈치, 손끝, 중심))
        거리.append(d - r - 링크_반지름)
    return np.min(거리, axis=0)


def 충돌(q: np.ndarray) -> bool:
    return bool(여유(q) < 0)


def 선분_충돌(q1: np.ndarray, q2: np.ndarray, 간격: float = 0.02) -> bool:
    """관절 공간의 곧은 선 q1→q2를 간격(rad)마다 잘라 한 곳이라도 부딪히면 True."""
    개수 = int(np.ceil(np.linalg.norm(q2 - q1) / 간격)) + 1
    t = np.linspace(0, 1, 개수)[:, None]
    return bool((여유(q1 + t * (q2 - q1)) < 0).any())


def 관절공간_지도(간격_도: int = 2) -> np.ndarray:
    """어깨·팔꿈치를 -180~180도에서 간격_도마다 훑어, 부딪히는 자세를 True로 표시한 표."""
    각도 = np.deg2rad(np.arange(-180, 181, 간격_도))
    어깨, 팔꿈치 = np.meshgrid(각도, 각도, indexing="ij")
    return 여유(np.stack([어깨, 팔꿈치], axis=-1)) < 0
