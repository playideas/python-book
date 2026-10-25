"""pyserial로 Feetech 서보 버스와 이야기하는 작은 클라이언트."""
import serial

import 페테크 as ft


class 통신실패(Exception):
    """재시도까지 다 했는데도 응답을 받지 못했다."""


class 서보버스:
    def __init__(self, 포트: str, 속도: int = 1_000_000, 시간_한계: float = 0.05, 재시도: int = 2) -> None:
        self.포트 = serial.Serial(포트, 속도, timeout=시간_한계)
        self.재시도 = 재시도
        self.통계 = {"시간 초과": 0, "체크섬 오류": 0}

    def _받기(self, 서보_id: int) -> bytes:
        머리 = self.포트.read(4)                         # FF FF ID 길이
        나머지 = self.포트.read(머리[3]) if len(머리) == 4 else b""
        if len(머리) < 4 or len(나머지) < 머리[3]:
            self.통계["시간 초과"] += 1
            raise 통신실패("시간 초과")
        try:
            응답_id, _, 데이터 = ft.응답_풀기(머리 + 나머지)
        except ft.패킷오류:
            self.통계["체크섬 오류"] += 1
            raise
        if 응답_id != 서보_id:
            raise ft.패킷오류("다른 서보의 응답")
        return 데이터

    def _주고받기(self, 서보_ids: list[int], 패킷: bytes) -> list[bytes]:
        """패킷을 보내고 서보마다 응답 하나씩 받는다. 하나라도 틀리면 통째로 다시 보낸다."""
        for _ in range(self.재시도 + 1):
            self.포트.reset_input_buffer()               # 지난번에 남은 찌꺼기를 버린다
            self.포트.write(패킷)
            try:
                return [self._받기(i) for i in 서보_ids]
            except (통신실패, ft.패킷오류):
                continue
        raise 통신실패(f"ID {서보_ids}: {self.재시도 + 1}번 보냈지만 응답이 없다")

    def 핑(self, 서보_id: int) -> bool:
        try:
            self._주고받기([서보_id], ft.명령_패킷(서보_id, ft.PING))
            return True
        except 통신실패:
            return False

    def 읽기(self, 서보_id: int, 레지스터: tuple[int, int]) -> int:
        [데이터] = self._주고받기([서보_id], ft.명령_패킷(서보_id, ft.READ, bytes(레지스터)))
        return ft.바이트_값(레지스터, 데이터)

    def 쓰기(self, 서보_id: int, 레지스터: tuple[int, int], 값: int) -> None:
        인자 = bytes([레지스터[0]]) + ft.값_바이트(레지스터, 값)
        self._주고받기([서보_id], ft.명령_패킷(서보_id, ft.WRITE, 인자))

    def 함께_쓰기(self, 레지스터: tuple[int, int], 값들: dict[int, int]) -> None:
        """SYNC_WRITE: 여러 서보에 한 패킷으로 쓴다. 서보는 답하지 않는다."""
        인자 = bytes(레지스터) + b"".join(bytes([i]) + ft.값_바이트(레지스터, v) for i, v in 값들.items())
        self.포트.write(ft.명령_패킷(ft.방송_ID, ft.SYNC_WRITE, 인자))

    def 함께_읽기(self, 레지스터: tuple[int, int], 서보_ids: list[int]) -> dict[int, int]:
        """SYNC_READ: 한 번 물으면 서보들이 ID 순서대로 답한다."""
        패킷 = ft.명령_패킷(ft.방송_ID, ft.SYNC_READ, bytes(레지스터) + bytes(서보_ids))
        답들 = self._주고받기(서보_ids, 패킷)
        return {i: ft.바이트_값(레지스터, 답) for i, 답 in zip(서보_ids, 답들)}
