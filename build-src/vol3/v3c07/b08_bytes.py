눈금 = 2388
print("작은 자리 먼저(little):", 눈금.to_bytes(2, "little").hex(" "))
print("큰 자리 먼저(big)   :", 눈금.to_bytes(2, "big").hex(" "))
print("거꾸로 읽으면       :", int.from_bytes(눈금.to_bytes(2, "little"), "big"))

# 음수 -100을 16비트로 적는 두 가지 방법
부호_크기 = 0x8000 | 100                          # 맨 위 비트는 부호, 나머지는 크기(Feetech 위치)
이의_보수 = -100 & 0xFFFF                         # 대부분의 칩과 파이썬 struct가 쓰는 방식
print(f"부호-크기 : {부호_크기:016b} = 0x{부호_크기:04x}")
print(f"2의 보수  : {이의_보수:016b} = 0x{이의_보수:04x}")
print("부호-크기를 2의 보수로 읽으면:", int.from_bytes(부호_크기.to_bytes(2, "little"), "little", signed=True))
