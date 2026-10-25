"""14장: 경로 추종(순수 추종, 스탠리)과, 바퀴가 늦게 따라오는 로봇으로 달려 보는 도구."""
import numpy as np

from 이동도구 import 각도_감싸기, 바퀴에서_속도, 속도에서_바퀴, 유니사이클_걸음


def 다시_찍기(점들: np.ndarray, 간격: float = 0.05) -> np.ndarray:
    """꺾은선 경로를 같은 간격의 점들로 다시 찍는다."""
    조각 = np.linalg.norm(np.diff(점들, axis=0), axis=1)
    누적 = np.concatenate([[0], np.cumsum(조각)])
    새_누적 = np.arange(0, 누적[-1], 간격)
    return np.column_stack([np.interp(새_누적, 누적, 점들[:, 0]), np.interp(새_누적, 누적, 점들[:, 1])])


def 가까운_번호(경로: np.ndarray, 위치, 이전: int = 0, 창: int = 40) -> int:
    """지난번 번호부터 앞으로 창 안에서 가장 가까운 경로 점(뒤로 돌아가지 않게)."""
    끝 = min(len(경로), 이전 + 창)
    return 이전 + int(np.argmin(np.linalg.norm(경로[이전:끝] - 위치, axis=1)))


def 순수_추종(포즈, 경로: np.ndarray, 번호: int, 앞_거리: float, v: float) -> tuple[float, float]:
    """앞_거리만큼 앞의 경로 점을 지나는 원호를 골라 (v, ω)를 낸다."""
    거리들 = np.linalg.norm(경로[번호:] - 포즈[:2], axis=1)
    넘은 = np.nonzero(거리들 >= 앞_거리)[0]
    목표 = 경로[번호 + 넘은[0]] if len(넘은) else 경로[-1]
    dx, dy = 목표 - 포즈[:2]
    알파 = 각도_감싸기(np.arctan2(dy, dx) - 포즈[2])     # 로봇 앞에서 잰 목표 방향
    곡률 = 2 * np.sin(알파) / max(np.hypot(dx, dy), 1e-6)
    return v, v * 곡률


def 스탠리(포즈, 경로: np.ndarray, 번호: int, v: float, k: float = 2.0) -> tuple[float, float]:
    """방향 오차와 옆 오차를 함께 줄인다. 원래 자동차 앞바퀴 조향각 식을 각속도로 바꿔 쓴다."""
    i = min(번호, len(경로) - 2)
    접선 = 경로[i + 1] - 경로[i]
    경로_방향 = np.arctan2(접선[1], 접선[0])
    dx, dy = 포즈[:2] - 경로[i]
    옆_오차 = np.cos(경로_방향) * dy - np.sin(경로_방향) * dx      # 경로 왼쪽이면 +
    조향 = 각도_감싸기(경로_방향 - 포즈[2]) + np.arctan2(-k * 옆_오차, v)
    return v, 2.5 * 조향


def 따라_달리기(경로: np.ndarray, 제어기, 시작_포즈, 지연: float = 0.15, 주기: float = 0.1,
            초: float = 60.0, ω_한계: float = 2.5, 위치_알기=None) -> np.ndarray:
    """주기마다 제어기(포즈, 경로, 번호)를 부르고, 바퀴는 지연(s)만큼 늦게 명령을 따라간다.
    위치_알기(참 포즈)를 주면 제어기는 참 포즈 대신 그 함수가 알려 준 포즈로 판단한다."""
    dt = 0.01
    포즈 = np.array(시작_포즈, dtype=float)
    바퀴 = np.zeros(2)                                   # 실제 바퀴 각속도(rad/s)
    명령 = np.zeros(2)
    번호, 궤적 = 0, [포즈]
    for k in range(round(초 / dt)):
        if k % round(주기 / dt) == 0:
            아는_포즈 = 위치_알기(포즈) if 위치_알기 else 포즈
            번호 = 가까운_번호(경로, 아는_포즈[:2], 번호)
            if 번호 >= len(경로) - 2 and np.linalg.norm(경로[-1] - 아는_포즈[:2]) < 0.1:
                break
            v, ω = 제어기(아는_포즈, 경로, 번호)
            명령 = np.array(속도에서_바퀴(v, float(np.clip(ω, -ω_한계, ω_한계))))
        바퀴 += (명령 - 바퀴) * dt / 지연                    # 1차 지연: 바퀴는 명령을 천천히 따라간다
        포즈 = 유니사이클_걸음(포즈, *바퀴에서_속도(*바퀴), dt)
        궤적.append(포즈)
    return np.array(궤적)


def 옆_오차들(경로: np.ndarray, 궤적: np.ndarray) -> np.ndarray:
    """궤적의 각 점에서 경로까지 가장 가까운 거리(m)."""
    return np.array([np.min(np.linalg.norm(경로 - p[:2], axis=1)) for p in 궤적])
