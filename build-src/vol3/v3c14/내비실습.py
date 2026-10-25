"""14.9절 실습: MuJoCo 방에서 전역 A*와 DWA로 여러 목적지를 차례로 돈다."""
import mujoco
import numpy as np

from 감시도구 import 도착했나, 진척_감시
from 동적창 import dwa
from 이동도구 import 각도_감싸기, 바퀴에서_속도, 속도에서_바퀴
from 주행장면 import 라이다, 로봇_포즈, 장면_만들기
from 지도도구 import a_star, 내접, 비용_지도, 지도_그리기, 지도_원점, 지도_크기, 해상도
from 추종도구 import 가까운_번호, 다시_찍기

제어_주기 = 0.1          # s. 10Hz로 재고, 판단하고, 명령한다
몸_반지름 = 0.18         # m. MuJoCo 로봇 몸통의 실제 반지름


def 사람_위치(t: float) -> list[float]:
    """아래 복도 가운데에서 위아래로 서성이는 사람(가장 빠를 때 0.24m/s)."""
    return [5.6, 1.4 + 0.6 * np.sin(0.4 * t), 0.0]


def 칸_번호들(점들: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    i, j = np.floor((점들 - 지도_원점) / 해상도).astype(int).T
    return np.clip(i, 0, 지도_크기[0] - 1), np.clip(j, 0, 지도_크기[1] - 1)


class 장애물_층:
    """라이다로 본 것을 지도 위에 기억한다. 레이가 끝난 칸은 칠하고, 지나간 칸은 지운다."""

    def __init__(self, 정적_찬칸: np.ndarray) -> None:
        self.정적 = 정적_찬칸
        self.본 = np.zeros_like(정적_찬칸)

    def 넣기(self, 로봇_xy: np.ndarray, 점들: np.ndarray) -> None:
        비율 = np.arange(0, 1, 0.01)
        표본 = 로봇_xy + 비율[None, :, None] * (점들 - 로봇_xy)[:, None, :]
        길이 = np.linalg.norm(점들 - 로봇_xy, axis=1)
        지나감 = 비율[None, :] * 길이[:, None] < 길이[:, None] - 0.1
        self.본[칸_번호들(표본[지나감])] = False
        self.본[칸_번호들(점들)] = True

    def 비용(self) -> np.ndarray:
        return 비용_지도(self.정적 | self.본)


def 경로_막혔나(경로: np.ndarray, 번호: int, 비용: np.ndarray) -> bool:
    return bool(np.any(비용[칸_번호들(경로[번호:])] >= 내접))


def 몰기(모델, 데이터, v: float, ω: float, 초: float) -> None:
    """바퀴 명령을 걸어 두고 초만큼 시뮬레이션을 진행한다(사람도 함께 움직인다)."""
    데이터.ctrl[:] = 속도에서_바퀴(v, ω)
    for _ in range(round(초 / 모델.opt.timestep)):
        데이터.mocap_pos[0] = 사람_위치(데이터.time)
        mujoco.mj_step(모델, 데이터)


def 부딪혔나(모델, 데이터) -> bool:
    """로봇(몸·바퀴)이 바닥이 아닌 무언가에 닿았는가."""
    로봇들 = {모델.body(이름).id for 이름 in ["로봇", "왼바퀴", "오른바퀴"]}
    for c in 데이터.contact[:데이터.ncon]:
        몸1, 몸2 = 모델.geom_bodyid[c.geom1], 모델.geom_bodyid[c.geom2]
        if (몸1 in 로봇들) != (몸2 in 로봇들) and 0 not in (c.geom1, c.geom2):
            return True
    return False


def 목적지_하나(모델, 데이터, 층: 장애물_층, 목표, 최대_초: float = 120.0, 최대_복구: int = 3) -> dict:
    """한 목적지까지: 재고(라이다) → 지도 갱신 → 필요하면 다시 계획 → DWA → 바퀴 명령.
    길을 못 찾거나 막히면 복구 행동을 하고, 복구를 최대_복구번 해도 안 되면 포기한다."""
    시작_시각, 경로, 번호 = 데이터.time, None, 0
    감시 = 진척_감시()
    기록 = {"궤적": [], "경로들": [], "최소_여유": np.inf, "다시_계획": 0, "복구": 0, "부딪힘": 0, "사건": []}
    while 데이터.time - 시작_시각 < 최대_초:
        포즈 = 로봇_포즈(데이터)
        점들 = 라이다(모델, 데이터)
        층.넣기(포즈[:2], 점들)
        기록["궤적"].append(포즈)
        기록["최소_여유"] = min(기록["최소_여유"], np.linalg.norm(점들 - 포즈[:2], axis=1).min() - 몸_반지름)
        if 도착했나(포즈, 목표):
            break
        비용 = 층.비용()
        if 경로 is None or 경로_막혔나(경로, 번호, 비용):
            찾은 = a_star(비용, 포즈[:2], 목표)
            경로, 번호 = (다시_찍기(찾은) if 찾은 is not None else None), 0
            기록["다시_계획"] += 1
            기록["사건"].append((데이터.time, "경로 계획" + (" 실패" if 경로 is None else "")))
            if 경로 is not None:
                기록["경로들"].append(경로)
        if 경로 is None or 감시.막혔나(포즈, 데이터.time):
            if 기록["복구"] == 최대_복구:
                기록["사건"].append((데이터.time, "포기"))
                break
            기록["사건"].append((데이터.time, "길 없음 → 복구" if 경로 is None else "진척 없음 → 복구"))
            몰기(모델, 데이터, -0.15, 0.0, 2.0)          # 복구 1: 0.3m 뒤로
            몰기(모델, 데이터, 0.0, 1.0, np.pi / 2)      # 복구 2: 제자리에서 90도
            기록["복구"] += 1
            경로 = None
            감시.다시(로봇_포즈(데이터), 데이터.time)
            continue
        번호 = 가까운_번호(경로, 포즈[:2], 번호)
        목표점 = 경로[min(번호 + 20, len(경로) - 1)]                  # 1m 앞의 경로 점
        방향_차 = 각도_감싸기(np.arctan2(*(목표점 - 포즈[:2])[::-1]) - 포즈[2])
        if abs(방향_차) > np.pi / 2:                                # 길이 뒤쪽이면 제자리에서 먼저 돈다
            몰기(모델, 데이터, 0.0, np.sign(방향_차) * 1.0, 제어_주기)
            continue
        지금_v, 지금_ω = 바퀴에서_속도(데이터.qvel[6], 데이터.qvel[7])   # 바퀴 엔코더로 잰 속도
        결과 = dwa(포즈, 지금_v, 지금_ω, 목표점, 점들)
        몰기(모델, 데이터, 결과["v"], 결과["ω"], 제어_주기)
        기록["부딪힘"] += 부딪혔나(모델, 데이터)
    기록["걸린_초"] = 데이터.time - 시작_시각
    기록["도착"] = 도착했나(로봇_포즈(데이터), 목표)
    기록["궤적"] = np.array(기록["궤적"])
    return 기록
