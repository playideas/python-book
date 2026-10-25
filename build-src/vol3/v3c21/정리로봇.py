"""21장: 1장의 감지·판단·행동 고리로 책상을 정리한다. 물건 하나를 옮길 때마다 다시 보고 다시 계획한다."""
import mujoco
import numpy as np

from 경로도구 import 제어_주기
from 작업판단 import 고르기, 빈_칸
from 잡기도구 import 역기구학, 요_고르기, 집기_포즈
from 집게 import 손가락_최대
from 집고놓기 import 단계, 집고놓기
from 책상인지 import 물건_찾기
from 책상장면 import 대기_자세, 물성, 상자들, 찍기
from 팔계획 import 계획, 충돌검사기
from 팔집게장면 import 집_자세

옮길_높이 = 0.08            # 상자 위 이만큼에서 내려놓기 시작한다(벽 3cm보다 넉넉히)


class 계획하는_집고놓기(집고놓기):
    """15장 상태 기계에서 접근과 옮기기만 장애물을 피하는 계획 경로로 바꾼다."""

    def __init__(self, 모델, 데이터, 물건: dict, 장애물: list[dict], 놓을_곳, 생성기):
        self.물건, self.장애물, self.생성기, self.길_없음 = 물건, 장애물, 생성기, False
        self.계획_기록: list[tuple[str, int, int]] = []         # (단계, 경유점 수, 충돌 검사 수)
        잡을_요 = 요_고르기(물건["중심"], 물건["요_도"], 집_자세)
        놓을_요 = 요_고르기(놓을_곳, 0.0, 집_자세)                 # 상자 안에서는 물건 길이를 x 방향으로
        super().__init__(모델, 데이터, 물건["중심"], 잡을_요, 놓을_곳, 놓을_요, 쥐는_힘=10.0)

    def 길(self, 곳, 위로: float, 요_도: float, 시간: float) -> list[np.ndarray]:
        if self.단계 not in (단계.접근, 단계.옮기기):
            return super().길(곳, 위로, 요_도, 시간)
        든_것 = self.물건 if self.단계 is 단계.옮기기 else None
        q_끝 = 역기구학(집기_포즈(곳 + [0, 0, 옮길_높이 if 든_것 else 위로], 요_도), 집_자세, 반복=200)
        검사기 = 충돌검사기(self.장애물, 든_것)
        경로 = 계획(self.데이터.ctrl[:6].copy(), q_끝, 검사기, self.생성기)
        self.계획_기록.append((self.단계.value, getattr(검사기, "경유점_수", 0), 검사기.검사_수))
        if 경로 is None:
            self.길_없음 = True
            return []
        return 경로 + [경로[-1]] * 20

    def 판단(self):
        if self.길_없음 and self.단계 is not 단계.실패:
            return 단계.실패, "길을 찾지 못함"
        return super().판단()


class 정리로봇:
    def __init__(self, 모델, 데이터, p: 물성 = 물성(), 씨앗: int = 0, 할_종류=tuple(상자들),
                 최대_시간: float = 240.0, 다시_보기: bool = True, 카메라_보정=(0.0, 0.0, 0.0)):
        self.모델, self.데이터, self.p = 모델, 데이터, p
        self.생성기 = np.random.default_rng(씨앗)
        self.할_종류, self.최대_시간, self.다시_보기 = 할_종류, 최대_시간, 다시_보기
        self.카메라_보정 = 카메라_보정
        self.기록: list[tuple[float, str, str]] = []
        self.실패_자리: list[np.ndarray] = []
        self.직전: tuple[dict, int] | None = None           # 방금 옮긴 물건과, 그때 그 종류 상자 안에 있던 수
        self.데이터.qpos[:6] = self.데이터.ctrl[:6] = 대기_자세
        self.데이터.ctrl[6] = 2 * 손가락_최대
        mujoco.mj_forward(모델, 데이터)

    def 적기(self, 무엇: str, 메모: str = "") -> None:
        self.기록.append((round(self.데이터.time, 1), 무엇, 메모))

    def 사진(self) -> tuple[np.ndarray, np.ndarray]:
        return 찍기(self.모델, self.데이터, self.p, self.생성기)

    def 감지(self) -> list[dict] | None:
        컬러, 깊이 = self.사진()
        if not np.all(np.isfinite(깊이)) or 깊이.max() <= 0:
            return None                                       # 사진이 이상하면 판단하지 않는다(감시견)
        return 물건_찾기(컬러, 깊이, self.카메라_보정)

    def 지켜보기(self, 작업=None) -> None:
        """제어 주기마다 불린다. 명령을 기록하거나 그림을 남기고 싶으면 이 메서드를 바꾼다."""

    def 따라가기(self, 경로: list[np.ndarray]) -> None:
        걸음 = int(round(제어_주기 / self.모델.opt.timestep))
        for q in 경로 + [경로[-1]] * 20:
            self.데이터.ctrl[:6] = q
            for _ in range(걸음):
                mujoco.mj_step(self.모델, self.데이터)
            self.지켜보기()

    def 행동(self, 물건: dict, 물건들: list[dict]) -> bool:
        """한 물건을 집어 종류별 상자에 놓고 대기 자세로 돌아온다."""
        장애물 = [다른 for 다른 in 물건들 if 다른 is not 물건]
        작업 = 계획하는_집고놓기(self.모델, self.데이터, 물건, 장애물, [*빈_칸(물건["종류"], 물건들), 물건["중심"][2]], self.생성기)
        성공 = 작업.실행(최대_시간=self.데이터.time + 30, 찍기=self.지켜보기)
        self.적기("옮기기" if 성공 else "실패", f"{물건['종류']}({물건['중심'][0]:.2f}, {물건['중심'][1]:.2f}) "
                                             f"{작업.기록[-1][2] or 작업.기록[-1][1]}")
        if not 성공:
            self.실패_자리.append(물건["중심"][:2])
        돌아갈_길 = 계획(self.데이터.ctrl[:6].copy(), 대기_자세, 충돌검사기(장애물), self.생성기)
        if 돌아갈_길 is None:
            raise RuntimeError("대기 자세로 돌아갈 길이 없다")
        self.따라가기(돌아갈_길)
        return 성공

    def 확인(self, 물건들: list[dict]) -> None:
        """방금 옮겼다는 물건이 정말 상자에 들어갔는지 새 사진으로 확인한다."""
        if self.직전 is None:
            return
        대상, 전 = self.직전
        지금 = sum(물건["종류"] == 대상["종류"] and 물건["자리"] == 대상["종류"] for 물건 in 물건들)
        if 지금 > 전:
            self.적기("확인", f"{대상['종류']} 상자 안 {전}개 → {지금}개")
        else:
            self.적기("확인 실패", f"{대상['종류']} 상자 안 {지금}개 그대로")
            self.실패_자리.append(대상["중심"][:2])
        self.직전 = None

    def 정리(self) -> list[tuple[float, str, str]]:
        """감지 → 판단 → 행동을 물건 하나마다 되풀이한다. 다시_보기=False면 처음 한 번만 본다."""
        물건들 = None
        while True:
            if self.데이터.time > self.최대_시간:
                self.적기("감시견", "시간 초과로 멈춤")
                break
            if 물건들 is None or self.다시_보기:
                if (물건들 := self.감지()) is None:
                    self.적기("감시견", "사진 이상으로 멈춤")
                    break
                self.확인(물건들)
            대상, 건너뜀 = 고르기(물건들, self.할_종류, self.실패_자리)
            if 대상 is None:
                self.적기("끝", " / ".join(건너뜀))
                break
            안 = sum(물건["종류"] == 대상["종류"] and 물건["자리"] == 대상["종류"] for 물건 in 물건들)
            self.직전 = (대상, 안) if self.행동(대상, 물건들) else None
            if not self.다시_보기:
                물건들 = [물건 for 물건 in 물건들 if 물건 is not 대상]
        return self.기록
