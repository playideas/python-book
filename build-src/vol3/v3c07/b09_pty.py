import os

import serial

주, 부 = os.openpty()                     # 가상 직렬 포트 한 쌍: 한쪽에 쓰면 다른 쪽에서 읽힌다
이름 = os.ttyname(부)
print("가상 포트 이름이 생겼다:", 이름.startswith("/dev/tty"))

포트 = serial.Serial(이름, baudrate=115_200, timeout=0.05)   # 실물이면 '/dev/ttyACM0', 'COM3' 같은 이름
포트.write(bytes([0xFF, 0xFF, 0x01, 0x02, 0x01, 0xFB]))
print("건너편이 받은 것:", os.read(주, 100).hex(" "))

os.write(주, bytes([0xFF, 0xFF, 0x01, 0x02, 0x00, 0xFC]))   # 건너편이 답장을 쓴다
print("포트에서 읽은 것:", 포트.read(6).hex(" "))
print("기다려도 안 오면:", 포트.read(6), "← timeout 뒤 빈 바이트")
