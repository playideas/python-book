"""18장: 시연을 모으고, 정책을 굴리고, 성공률을 재는 도구."""
import os
from pathlib import Path

import numpy as np

from 모방환경 import 집고놓기환경, 상자_범위, 최대_걸음
from 전문가 import 전문가

저장_폴더 = Path(os.environ.get("BOOK_DATA_DIR", "data")) / "ch18"


def 굴리기(상자_위치, 정책=None, 물어보기: bool = False, 흔들림: float = 0.0, 씨앗: int = 0, 찍기=None):
    """에피소드 하나. 정책이 없으면 전문가가 움직인다.
    물어보기=True면 정책이 움직이는 동안 들른 상태마다 전문가의 답을 함께 적는다(DAgger)."""
    환경 = 집고놓기환경(상자_위치, 흔들림, 씨앗)
    관측들, 전문가_행동들 = [], []
    while 환경.걸음 < 최대_걸음 and not 환경.끝났나() and not 환경.망쳤나():
        관측 = 환경.관측()
        답 = 전문가(환경) if 정책 is None or 물어보기 else None
        관측들.append(관측)
        전문가_행동들.append(답)
        환경.한걸음(답 if 정책 is None else 정책(관측))
        if 찍기 is not None:
            찍기(환경)
    행동들 = np.array(전문가_행동들) if 전문가_행동들[0] is not None else None
    return np.array(관측들), 행동들, 환경.끝났나()


def 시연_모으기(개수: int, 씨앗: int = 0) -> dict[str, np.ndarray]:
    """전문가 시연 개수만큼. 한 번 만든 것은 저장해 두고 다시 읽는다."""
    파일 = 저장_폴더 / f"demos_{개수}_{씨앗}.npz"
    if 파일.exists():
        return dict(np.load(파일))
    생성기 = np.random.default_rng(씨앗)
    관측, 행동, 번호 = [], [], []
    for i in range(개수):
        o, a, _ = 굴리기(생성기.uniform(*상자_범위))
        관측.append(o)
        행동.append(a)
        번호.append(np.full(len(o), i))
    데이터 = {"관측": np.concatenate(관측), "행동": np.concatenate(행동), "에피소드": np.concatenate(번호)}
    저장_폴더.mkdir(parents=True, exist_ok=True)
    np.savez(파일, **데이터)
    return 데이터


def 시험_위치(개수: int = 50) -> np.ndarray:
    """학습에 쓰지 않은 상자 위치. 모든 정책을 같은 위치에서 시험한다."""
    return np.random.default_rng(1000).uniform(*상자_범위, size=(개수, 2))


def 성공률(정책, 위치들, 흔들림: float = 0.0) -> float:
    return float(np.mean([굴리기(p, 정책, 흔들림=흔들림, 씨앗=i)[2] for i, p in enumerate(위치들)]))
