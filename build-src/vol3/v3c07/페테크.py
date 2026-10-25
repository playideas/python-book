"""Feetech STS 서보 프로토콜: 패킷 만들기·풀기와 STS3215의 주요 레지스터."""

# 명령(instruction) 번호
PING, READ, WRITE, SYNC_READ, SYNC_WRITE = 0x01, 0x02, 0x03, 0x82, 0x83
방송_ID = 0xFE                    # 버스 위의 모든 서보에게 보낼 때 쓰는 ID

# STS3215 레지스터: (주소, 바이트 수)
모델번호 = (3, 2)
아이디 = (5, 1)
최소_위치 = (9, 2)
최대_위치 = (11, 2)
영점_보정 = (31, 2)               # Homing_Offset
토크_켜기 = (40, 1)
목표_위치 = (42, 2)
잠금 = (55, 1)
현재_위치 = (56, 2)

# 음수를 '부호-크기'로 적는 레지스터와 그 부호 비트 번호
부호_비트 = {영점_보정: 11, 목표_위치: 15, 현재_위치: 15}


class 패킷오류(Exception):
    """머리나 체크섬이 맞지 않는 패킷."""


def 체크섬(몸통: bytes) -> int:
    """ID부터 마지막 매개변수까지 더한 값의 아래 8비트를 뒤집는다."""
    return ~sum(몸통) & 0xFF


def 명령_패킷(서보_id: int, 명령: int, 매개변수: bytes = b"") -> bytes:
    """FF FF | ID | 길이 | 명령 | 매개변수... | 체크섬. 길이 = 매개변수 수 + 2."""
    몸통 = bytes([서보_id, len(매개변수) + 2, 명령]) + bytes(매개변수)
    return b"\xff\xff" + 몸통 + bytes([체크섬(몸통)])


def 응답_풀기(패킷: bytes) -> tuple[int, int, bytes]:
    """서보의 응답(상태 패킷)에서 (ID, 오류 바이트, 매개변수)를 꺼낸다."""
    if len(패킷) < 6 or 패킷[:2] != b"\xff\xff":
        raise 패킷오류("머리가 틀렸다")
    if 체크섬(패킷[2:-1]) != 패킷[-1]:
        raise 패킷오류("체크섬이 틀렸다")
    return 패킷[2], 패킷[4], bytes(패킷[5:-1])


def 값_바이트(레지스터: tuple[int, int], 값: int) -> bytes:
    """정수를 레지스터 크기의 바이트로. 작은 자리가 먼저(little-endian)."""
    비트 = 부호_비트.get(레지스터)
    if 비트 is not None and 값 < 0:
        값 = -값 | 2 ** 비트                   # 부호-크기: 부호 비트만 켜고 크기는 그대로
    return int(값).to_bytes(레지스터[1], "little")


def 바이트_값(레지스터: tuple[int, int], 데이터: bytes) -> int:
    """값_바이트의 반대."""
    값 = int.from_bytes(데이터, "little")
    비트 = 부호_비트.get(레지스터)
    if 비트 is not None and 값 & 2 ** 비트:
        값 = -(값 & (2 ** 비트 - 1))
    return 값
