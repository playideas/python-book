"""15장: 집고-놓기를 상태 기계로. 단계마다 들어갈 때 할 일과 넘어갈 조건을 적는다."""
from enum import Enum

import mujoco
import numpy as np

from 경로도구 import 제어_주기, 직선_경로
from 잡기도구 import TCP_포즈, 집기_포즈
from 집게 import 손가락_최대

접근_높이 = 0.10          # 잡을 곳 위 10cm에서 멈췄다가 곧게 내려간다(사전 접근 자세)
들기_높이 = 0.15
부딪힘_힘 = 2.0           # 내려가는 중 손목 힘이 이만큼(N) 변하면 무언가에 부딪힌 것
닿음_비율 = 0.5           # 두 손가락이 모두 쥐는 힘의 절반 이상을 느껴야 잡은 것
최소_너비 = 0.01          # 손가락이 1cm보다 좁게 닫히면 빈손


class 단계(Enum):
    접근 = "접근"
    내려가기 = "내려가기"
    쥐기 = "쥐기"
    들기 = "들기"
    옮기기 = "옮기기"
    내려놓기 = "내려놓기"
    놓기 = "놓기"
    물러나기 = "물러나기"
    완료 = "완료"
    실패 = "실패"


class 집고놓기:
    def __init__(self, 모델, 데이터, 잡을_곳, 잡을_요_도, 놓을_곳, 놓을_요_도, 쥐는_힘):
        self.모델, self.데이터 = 모델, 데이터
        self.잡을_곳, self.잡을_요_도 = np.asarray(잡을_곳, dtype=float), 잡을_요_도
        self.놓을_곳, self.놓을_요_도 = np.asarray(놓을_곳, dtype=float), 놓을_요_도
        self.쥐는_힘 = 쥐는_힘
        self.기록: list[tuple[float, str, str]] = []
        self.바꾸기(단계.접근)

    def 손목_힘(self) -> np.ndarray:
        return self.데이터.sensor("wrist_force").data.copy()

    def 잡고_있나(self) -> bool:
        닿음 = min(self.데이터.sensor("touch_l").data[0], self.데이터.sensor("touch_r").data[0])
        return 닿음 > 닿음_비율 * self.쥐는_힘 and self.데이터.sensor("width").data[0] > 최소_너비

    def 길(self, 곳, 위로: float, 요_도: float, 시간: float) -> list[np.ndarray]:
        """지금 관절 목표에서 '곳 위 위로 m' 포즈까지 직선 경로. 끝에 0.2초 머문다."""
        경로 = 직선_경로(self.데이터.ctrl[:6].copy(), 집기_포즈(곳 + [0, 0, 위로], 요_도), 시간)
        return 경로 + [경로[-1]] * 20

    def 바꾸기(self, 새_단계: 단계, 메모: str = "") -> None:
        """단계를 바꾸고, 그 단계에 들어가며 할 일(경로·집게 명령)을 정한다."""
        self.단계, self.시작 = 새_단계, self.데이터.time
        self.기록.append((round(self.데이터.time, 2), 새_단계.value, 메모))
        잡, 놓 = (self.잡을_곳, self.잡을_요_도), (self.놓을_곳, self.놓을_요_도)
        self.경로 = {단계.접근: lambda: self.길(잡[0], 접근_높이, 잡[1], 2.0),
                   단계.내려가기: lambda: self.길(잡[0], 0.0, 잡[1], 1.0),
                   단계.들기: lambda: self.길(잡[0], 들기_높이, 잡[1], 1.0),
                   단계.옮기기: lambda: self.길(놓[0], 0.05, 놓[1], 2.0),
                   단계.내려놓기: lambda: self.길(놓[0], -0.03, 놓[1], 1.6),   # 일부러 3cm 더 아래까지
                   단계.물러나기: lambda: self.길(TCP_포즈(self.데이터.ctrl[:6])[:3, 3], 접근_높이, 놓[1], 1.0),
                   단계.실패: lambda: self.길(TCP_포즈(self.데이터.ctrl[:6])[:3, 3], 접근_높이, 잡[1], 1.0),
                   }.get(새_단계, lambda: [])()
        if 새_단계 is 단계.내려가기:
            self.영점 = self.손목_힘()                  # 빈손일 때의 손목 힘(집게 무게)을 영점으로
        if 새_단계 is 단계.쥐기:
            self.데이터.ctrl[6] = 0.0                    # 끝까지 닫으라고 명령: 힘은 forcerange까지만
        if 새_단계 in (단계.놓기, 단계.실패):
            self.데이터.ctrl[6] = 2 * 손가락_최대

    def 판단(self) -> tuple[단계, str] | None:
        """지금 단계가 끝났는지, 끝났다면 다음 단계는 무엇인지."""
        s, 남은_길, 지난 = self.단계, len(self.경로), self.데이터.time - self.시작
        변화 = self.손목_힘() - self.영점 if hasattr(self, "영점") else np.zeros(3)
        힘_변화, 하중 = np.linalg.norm(변화), -변화[2]     # 손목 z축은 아래(손가락 쪽)를 본다
        if s is 단계.내려가기 and 힘_변화 > 부딪힘_힘:
            return 단계.실패, f"내려가다 부딪힘({힘_변화:.1f}N)"
        if s in (단계.들기, 단계.옮기기) and not self.잡고_있나():
            return 단계.실패, "들고 가다 놓침"
        if s is 단계.쥐기 and 지난 > 0.5:
            너비_cm = self.데이터.sensor("width").data[0] * 100
            return (단계.들기, f"너비 {너비_cm:.1f}cm") if self.잡고_있나() else (단계.실패, f"빈손(너비 {너비_cm:.1f}cm)")
        if s is 단계.내려놓기 and 하중 < 0.5 * self.무게_힘:
            self.데이터.ctrl[:6] = self.데이터.qpos[:6]  # 무게 절반이 탁자로 넘어갔다: 그 자리에 멈춘다
            return 단계.놓기, f"탁자에 닿음(TCP 높이 {self.데이터.site('tcp').xpos[2]:.3f}m)"
        if s is 단계.놓기 and 지난 > 0.4:
            return 단계.물러나기, ""
        if 남은_길 == 0 and s in (단계.접근, 단계.내려가기, 단계.들기, 단계.옮기기, 단계.내려놓기, 단계.물러나기):
            if s is 단계.들기:
                self.무게_힘 = 하중
                return 단계.옮기기, f"무게 {하중 / 9.81:.3f}kg"
            다음 = {단계.접근: 단계.내려가기, 단계.내려가기: 단계.쥐기, 단계.옮기기: 단계.내려놓기,
                  단계.내려놓기: 단계.놓기, 단계.물러나기: 단계.완료}[s]
            return 다음, ""
        return None

    def 실행(self, 최대_시간: float = 20.0, 찍기=None) -> bool:
        """제어 주기마다 경로를 한 칸 보내고 판단한다. 완료면 True."""
        걸음 = int(round(제어_주기 / self.모델.opt.timestep))
        while not (self.단계 in (단계.완료, 단계.실패) and not self.경로):
            if self.경로:
                self.데이터.ctrl[:6] = self.경로.pop(0)
            if (다음 := self.판단()) is not None:
                self.바꾸기(*다음)
            for _ in range(걸음):
                mujoco.mj_step(self.모델, self.데이터)
            if 찍기 is not None:
                찍기(self)
            if self.데이터.time > 최대_시간 and self.단계 is not 단계.실패:
                self.바꾸기(단계.실패, "시간 초과")
        return self.단계 is 단계.완료
