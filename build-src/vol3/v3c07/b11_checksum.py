import 페테크 as ft

응답 = bytes.fromhex("FF FF 01 04 00 50 08 A2")


def 통과하나(패킷: bytes) -> bool:
    try:
        ft.응답_풀기(패킷)
        return True
    except ft.패킷오류:
        return False


# 1) 비트 하나가 뒤집힌 경우: 머리 뒤의 모든 비트를 하나씩 뒤집어 본다
놓친 = 0
for 자리 in range(2, len(응답)):
    for 비트 in range(8):
        깨진 = bytearray(응답)
        깨진[자리] ^= 2 ** 비트
        놓친 += 통과하나(bytes(깨진))
print(f"비트 하나 오류 {(len(응답) - 2) * 8}가지 중 체크섬이 놓친 것: {놓친}")

# 2) 바이트 두 개의 자리가 바뀐 경우: 위치 0x0850(2128)이 0x5008이 된다
바뀐 = bytearray(응답)
바뀐[5], 바뀐[6] = 바뀐[6], 바뀐[5]
print("두 바이트 자리 바꿈 통과?", 통과하나(bytes(바뀐)),
      "→ 읽힌 위치", ft.바이트_값(ft.현재_위치, bytes(바뀐[5:7])))

# 3) 한 바이트는 +1, 다른 바이트는 -1
상쇄 = bytearray(응답)
상쇄[5] += 1
상쇄[6] -= 1
print("+1과 -1이 겹친 오류 통과?", 통과하나(bytes(상쇄)))
