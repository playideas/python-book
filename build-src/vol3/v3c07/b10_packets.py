import 페테크 as ft


def 보기(패킷: bytes) -> str:
    return 패킷.hex(" ").upper()


# 공개 구현(rustypot)의 시험에 적힌 기대 바이트와 비교한다
시험들 = [
    ("PING ID 1", ft.명령_패킷(1, ft.PING), "FF FF 01 02 01 FB"),
    ("READ ID 1, 주소 0x2B, 1바이트", ft.명령_패킷(1, ft.READ, bytes([0x2B, 1])), "FF FF 01 04 02 2B 01 CC"),
    ("SYNC_WRITE ID 11·12, 주소 30, 2바이트",
     ft.명령_패킷(ft.방송_ID, ft.SYNC_WRITE, bytes([30, 2, 11, 0x00, 0x00, 12, 0x0A, 0x14])),
     "FF FF FE 0A 83 1E 02 0B 00 00 0C 0A 14 1F"),
]
for 이름, 패킷, 기대 in 시험들:
    print(f"{이름}: {보기(패킷)} {'[O]' if 보기(패킷) == 기대 else '[X]'}")

# 이 장에서 자주 쓸 두 가지: 목표 위치 쓰기, 현재 위치 읽기
print("ID 1 목표 위치 ← 2388:", 보기(ft.명령_패킷(1, ft.WRITE, bytes([42]) + ft.값_바이트(ft.목표_위치, 2388))))
print("ID 1 현재 위치 읽기  :", 보기(ft.명령_패킷(1, ft.READ, bytes(ft.현재_위치))))

# 서보의 응답 풀기: ID 1, 오류 0, 매개변수 2바이트(현재 위치)
응답 = bytes.fromhex("FF FF 01 04 00 50 08 A2")
서보_id, 오류, 데이터 = ft.응답_풀기(응답)
print(f"응답: ID {서보_id}, 오류 {오류}, 현재 위치 {ft.바이트_값(ft.현재_위치, 데이터)}")
