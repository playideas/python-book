"""가상 직렬 포트(pty) 건너편에서 도는 가짜 Feetech 서보 버스. 키트 없이 7장 예제를 돌린다."""
import os
import select
import threading
import time

import numpy as np

import 페테크 as ft

물리_간격 = 0.001                     # 가짜 모터를 1ms씩 움직인다


class 가상시계:
    """제어 고리가 진행()을 부를 때만 흐르는 시계. 그래서 실행할 때마다 결과가 같다."""

    def __init__(self) -> None:
        self.지금 = 0.0
        self.버스들: list["가짜버스"] = []

    def 진행(self, 초: float) -> None:
        for 버스 in self.버스들:
            버스.따라잡기(초)
        self.지금 += 초


class 가짜서보:
    """레지스터 메모리 + 목표를 서서히 따라가는 모터(1차 지연과 속도 한계, 값은 예시)."""

    def __init__(self, 서보_id: int, 실제_위치: float = 2048.0,
                 시간_상수: float = 0.05, 최대_속도: float = 3000.0) -> None:
        self.id = 서보_id
        self.메모리 = bytearray(70)
        self.실제_위치 = 실제_위치          # 축이 실제로 놓인 곳(눈금). 영점 보정과 상관없다
        self.시간_상수, self.최대_속도 = 시간_상수, 최대_속도   # 초, 눈금/초
        self.쓰기(ft.모델번호, 777)          # LeRobot 표에 적힌 STS3215의 모델 번호
        self.쓰기(ft.아이디, 서보_id)
        self.쓰기(ft.최대_위치, 4095)
        self.현재_갱신()
        self.쓰기(ft.목표_위치, self.읽기(ft.현재_위치))

    def 읽기(self, 레지스터: tuple[int, int]) -> int:
        주소, 크기 = 레지스터
        return ft.바이트_값(레지스터, self.메모리[주소:주소 + 크기])

    def 쓰기(self, 레지스터: tuple[int, int], 값: int) -> None:
        주소, 크기 = 레지스터
        self.메모리[주소:주소 + 크기] = ft.값_바이트(레지스터, 값)

    def 현재_갱신(self) -> None:
        # 서보가 알려 주는 위치 = 실제 위치 - 영점 보정 (한 바퀴 4096눈금 안으로)
        self.쓰기(ft.현재_위치, round(self.실제_위치 - self.읽기(ft.영점_보정)) % 4096)

    def 움직이기(self, 간격: float) -> None:
        if self.읽기(ft.토크_켜기):
            목표 = np.clip(self.읽기(ft.목표_위치), self.읽기(ft.최소_위치), self.읽기(ft.최대_위치))
            남은 = 목표 + self.읽기(ft.영점_보정) - self.실제_위치
            속도 = np.clip(남은 / self.시간_상수, -self.최대_속도, self.최대_속도)
            self.실제_위치 += 속도 * 간격
        self.현재_갱신()

    def 손으로_돌리기(self, 실제_위치: float) -> None:
        """토크가 꺼진 서보를 사람이 손으로 돌려 놓는 것을 흉내 낸다."""
        assert not self.읽기(ft.토크_켜기), "토크가 켜진 서보는 손으로 돌릴 수 없다"
        self.실제_위치 = 실제_위치
        self.현재_갱신()


class 가짜버스:
    """pty 한쪽 끝에서 패킷을 받아 서보들에게 나눠 주고, 응답을 돌려보낸다."""

    def __init__(self, 서보들: list[가짜서보], 시계: 가상시계, 손실률: float = 0.0,
                 깨짐률: float = 0.0, 끊김: tuple[float, float] | None = None, 씨앗: int = 0) -> None:
        self.서보들 = {서보.id: 서보 for 서보 in 서보들}
        self.시계 = 시계
        시계.버스들.append(self)
        self.손실률, self.깨짐률, self.끊김 = 손실률, 깨짐률, 끊김
        self.생성기 = np.random.default_rng(씨앗)
        self._주, self._부 = os.openpty()      # 가상 직렬 포트 한 쌍
        self.포트_이름 = os.ttyname(self._부)  # 파이썬 프로그램은 이 이름을 연다
        self._잠금 = threading.Lock()
        self._받은 = bytearray()
        threading.Thread(target=self._돌기, daemon=True).start()

    def _돌기(self) -> None:
        while True:
            select.select([self._주], [], [])
            with self._잠금:
                self._받은 += os.read(self._주, 4096)
                while len(self._받은) >= 4 and len(self._받은) >= 4 + self._받은[3]:
                    길이 = 4 + self._받은[3]
                    패킷, self._받은 = bytes(self._받은[:길이]), self._받은[길이:]
                    if 응답 := self._처리(패킷):
                        os.write(self._주, 응답)          # 응답들은 한 번에 내보낸다

    def _처리(self, 패킷: bytes) -> bytes:
        if self.끊김 and self.끊김[0] <= self.시계.지금 < self.끊김[1]:
            return b""                                # 선이 빠졌다: 아무것도 닿지 않는다
        서보_id, 명령, 인자 = 패킷[2], 패킷[4], 패킷[5:-1]
        응답 = b""
        if 명령 == ft.SYNC_WRITE:                       # 주소, 크기, (ID, 데이터...)...
            주소, 크기 = 인자[0], 인자[1]
            for i in range(2, len(인자), 크기 + 1):
                if 인자[i] in self.서보들:
                    self.서보들[인자[i]].메모리[주소:주소 + 크기] = 인자[i + 1:i + 1 + 크기]
        elif 명령 == ft.SYNC_READ:                      # 주소, 크기, ID...: ID 순서대로 답한다
            for i in 인자[2:]:
                if i in self.서보들:
                    응답 += self._답(i, self.서보들[i].메모리[인자[0]:인자[0] + 인자[1]])
        elif 서보_id in self.서보들:                   # 없는 ID에는 아무도 답하지 않는다
            서보 = self.서보들[서보_id]
            if 명령 == ft.READ:
                return self._답(서보_id, 서보.메모리[인자[0]:인자[0] + 인자[1]])
            if 명령 == ft.WRITE:
                서보.메모리[인자[0]:인자[0] + len(인자) - 1] = 인자[1:]
            응답 = self._답(서보_id, b"")                # PING과 WRITE는 빈 응답
        for 서보 in self.서보들.values():
            서보.현재_갱신()                            # 영점 보정을 바꿨다면 바로 반영된다
        return 응답

    def _답(self, 서보_id: int, 데이터: bytes) -> bytes:
        응답 = bytearray(ft.명령_패킷(서보_id, 0, 데이터))   # 생김새가 같다. 명령 자리에 오류 바이트 0
        주사위 = self.생성기.random()
        if 주사위 < self.손실률:
            return b""                                # 응답이 사라졌다
        if 주사위 < self.손실률 + self.깨짐률:
            응답[-2] ^= 0x10                           # 잡음으로 비트 하나가 뒤집혔다
        return bytes(응답)

    def 따라잡기(self, 초: float) -> None:
        """도착한 명령을 모두 처리한 뒤, 서보들을 '초'만큼 움직인다."""
        while True:
            with self._잠금:
                if not select.select([self._주], [], [], 0)[0]:
                    for _ in range(round(초 / 물리_간격)):
                        for 서보 in self.서보들.values():
                            서보.움직이기(물리_간격)
                    return
            time.sleep(0.0002)                         # 아직 읽지 않은 명령이 있다: 잠깐 양보
