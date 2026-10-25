import numpy as np

# 시뮬레이션이라면: 데이터.ctrl[0] = np.deg2rad(30) 한 줄로 끝난다
각도_rad = np.deg2rad(30)

# 진짜 서보에게는: 각도를 서보의 눈금으로 바꾸고(한 바퀴 = 4096눈금, 가운데 = 2047)
눈금 = round(2047 + 각도_rad * 4096 / (2 * np.pi))
# '1번 서보야, 42번 칸(목표 위치)에 이 값을 써라'를 바이트로 적는다
몸통 = bytes([1, 5, 0x03, 42]) + 눈금.to_bytes(2, "little")
패킷 = b"\xff\xff" + 몸통 + bytes([~sum(몸통) & 0xFF])

print("눈금:", 눈금)
print("전선으로 나가는 바이트:", 패킷.hex(" "), f"({len(패킷)}바이트)")
