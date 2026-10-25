"""21장: 책상 위 물건 목록에서 다음에 옮길 물건을 고른다. 못 옮기는 물건은 까닭과 함께 건너뛴다."""
import numpy as np

from 잡기도구 import TCP_포즈, 역기구학, 집기_포즈
from 집게 import 손가락_최대
from 집고놓기 import 들기_높이
from 책상장면 import 상자들, 칸들
from 팔집게장면 import 집_자세

최대_시도 = 2                                   # 같은 자리의 물건에 이만큼 실패하면 건드리지 않는다
집을_수_있는_폭 = 2 * 손가락_최대 - 0.01        # 손가락을 다 벌려도 1cm는 남아야 한다(19장)


def 닿나(위치) -> bool:
    """손가락을 아래로 한 채 위치와 들기 높이까지 닿는가(19장 계획도구.py와 같다)."""
    for 위로 in (0.0, 들기_높이):
        T = 집기_포즈(np.asarray(위치) + [0, 0, 위로], 0.0)
        if np.linalg.norm(T[:3, 3] - TCP_포즈(역기구학(T, 집_자세, 반복=200))[:3, 3]) > 0.001:
            return False
    return True


def 손가락_막힘(물건: dict, 물건들: list[dict]) -> bool:
    """손가락을 다 벌렸을 때 두 손가락 자리(물건의 폭 방향 양쪽)에 다른 물건이 걸리는가."""
    ψ = np.deg2rad(물건["요_도"])
    for 부호 in (1, -1):
        손가락 = 물건["중심"][:2] + 부호 * (손가락_최대 + 0.006) * np.array([-np.sin(ψ), np.cos(ψ)])
        for 다른 in (다른 for 다른 in 물건들 if 다른 is not 물건):
            φ = np.deg2rad(다른["요_도"])
            x, y = np.array([[np.cos(φ), np.sin(φ)], [-np.sin(φ), np.cos(φ)]]) @ (손가락 - 다른["중심"][:2])
            if abs(x) < 다른["길이"] / 2 + 0.015 and abs(y) < 다른["폭"] / 2 + 0.01:   # 다른 물건 틀에서 본 손가락
                return True
    return False


def 빈_칸(종류: str, 물건들: list[dict]) -> np.ndarray | None:
    """그 종류 상자에서 아무 물건도 3cm 안에 없는 첫 칸(세계 기준 xy)."""
    for 칸 in 칸들:
        if all(np.linalg.norm(물건["중심"][:2] - (상자들[종류] + 칸)) > 0.03 for 물건 in 물건들):
            return 상자들[종류] + 칸
    return None


def 못_옮기는_까닭(물건: dict, 물건들: list[dict], 할_종류, 실패_자리: list) -> str:
    """빈 글이면 옮겨도 된다. 싼 검사부터 하고, 역기구학이 드는 검사는 뒤에 둔다."""
    if 물건["종류"] not in 할_종류:
        return "정리 규칙에 없는 종류"
    if sum(np.linalg.norm(물건["중심"][:2] - 곳) < 0.03 for 곳 in 실패_자리) >= 최대_시도:
        return f"{최대_시도}번 실패"
    if 빈_칸(물건["종류"], 물건들) is None:
        return "상자가 가득 참"
    if 물건["폭"] > 집을_수_있는_폭:
        return "집게보다 넓음"
    if 손가락_막힘(물건, 물건들):
        return "손가락 자리가 막힘"
    if not 닿나(물건["중심"]):
        return "팔이 닿지 않음"
    return ""


def 고르기(물건들: list[dict], 할_종류, 실패_자리: list) -> tuple[dict | None, list[str]]:
    """책상 위에서 옮길 수 있는 물건 중 받침(로봇)에 가장 가까운 것, 그리고 건너뛴 물건과 까닭."""
    후보, 건너뜀 = [], []
    for 물건 in (물건 for 물건 in 물건들 if 물건["자리"] == "책상"):
        if 까닭 := 못_옮기는_까닭(물건, 물건들, 할_종류, 실패_자리):
            건너뜀.append(f"{물건['종류']}({물건['중심'][0]:.2f}, {물건['중심'][1]:.2f}) {까닭}")
        else:
            후보.append(물건)
    return min(후보, key=lambda 물건: np.linalg.norm(물건["중심"][:2]), default=None), 건너뜀
