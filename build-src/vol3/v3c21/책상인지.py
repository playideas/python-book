"""21장: 9장의 색 분할과 깊이로 물건을 모두 찾고, 가운데·요·크기를 잰다(19장 상자_재기를 색 덩어리에)."""
import cv2
import numpy as np

from 색찾기 import 색_마스크
from 책상장면 import 높이, 너비, 바라보기, 상자_안쪽, 상자들, 종류들, 책상_높이, 카메라_fovy, 카메라_목표, 카메라_위치

최소_점수 = 150                       # 이보다 점이 적은 덩어리는 티끌이나 가려진 조각으로 본다


def 점구름(깊이: np.ndarray) -> np.ndarray:
    """깊이 사진의 픽셀마다 세계 기준 3차원 점. 카메라 포즈는 로봇이 '아는' 값(보정 결과)을 쓴다."""
    f = (높이 / 2) / np.tan(np.deg2rad(카메라_fovy) / 2)
    v, u = np.indices(깊이.shape)
    점_광학 = np.stack([(u - (너비 - 1) / 2) / f * 깊이, (v - (높이 - 1) / 2) / f * 깊이, 깊이], axis=-1)
    return 점_광학 @ 바라보기(카메라_위치, 카메라_목표).T + 카메라_위치


def 덩어리_재기(점들: np.ndarray) -> dict | None:
    """덩어리의 점에서 윗면을 골라 주성분 분석으로 가운데·요·길이·폭·높이를 잰다(15장 15.3절)."""
    위 = 점들[점들[:, 2] > 책상_높이 + 0.01]
    if len(위) < 20:
        return None
    윗면_높이 = np.percentile(위[:, 2], 90)
    윗면 = 위[위[:, 2] > 윗면_높이 - 0.005][:, :2]
    중심 = 윗면.mean(axis=0)
    _, 고유벡터 = np.linalg.eigh(np.cov((윗면 - 중심).T))
    투영 = (윗면 - 중심) @ 고유벡터
    return {"중심": np.array([*중심, (책상_높이 + 윗면_높이) / 2]),
            "요_도": float(np.rad2deg(np.arctan2(고유벡터[1, 1], 고유벡터[0, 1]))),
            "길이": float(np.ptp(투영[:, 1])), "폭": float(np.ptp(투영[:, 0])), "높이": float(윗면_높이 - 책상_높이)}


def 어느_상자(중심) -> str | None:
    """가운데가 정리 상자 안쪽에 있으면 그 상자의 종류."""
    return next((종류 for 종류, 곳 in 상자들.items() if np.all(np.abs(중심[:2] - 곳) < 상자_안쪽)), None)


def 위에서_나누기(점들: np.ndarray, 칸: float = 0.005) -> list[np.ndarray]:
    """책상보다 높은 점을 위에서 내려다본 격자에 찍고 이어진 칸끼리 묶는다.
    사진에서는 앞뒤로 겹쳐 한 덩어리로 보여도, 책상 위에서 떨어져 있으면 따로 나뉜다."""
    위 = 점들[점들[:, 2] > 책상_높이 + 0.01]
    if len(위) == 0:
        return []
    칸번호 = np.floor((위[:, :2] - 위[:, :2].min(axis=0)) / 칸).astype(int)
    격자 = np.zeros(칸번호.max(axis=0) + 1, np.uint8)
    격자[칸번호[:, 0], 칸번호[:, 1]] = 255
    격자 = cv2.morphologyEx(격자, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))   # 표본 사이 빈칸 메우기
    _, 표시 = cv2.connectedComponents(격자)
    묶음 = 표시[칸번호[:, 0], 칸번호[:, 1]]
    return [위[묶음 == k] for k in np.unique(묶음) if k > 0]


def 물건_찾기(컬러: np.ndarray, 깊이: np.ndarray, 보정=(0.0, 0.0, 0.0)) -> list[dict]:
    """색마다 물건을 모두 찾아 잰다. 책상 위 물건과 상자 안 물건을 '자리'로 나눈다.
    보정: 알려진 자리의 물건을 재서 얻은 치우침(m). 잰 점에서 빼 준다(21.7절)."""
    점들 = 점구름(깊이) - np.asarray(보정)
    물건들 = []
    for 종류 in 종류들:
        for 덩어리 in 위에서_나누기(점들[색_마스크(컬러, 종류) > 0]):
            if len(덩어리) >= 최소_점수 and (잰 := 덩어리_재기(덩어리)) is not None:
                물건들.append({"종류": 종류, **잰, "자리": 어느_상자(잰["중심"]) or "책상"})
    return 물건들
