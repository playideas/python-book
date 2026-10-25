import numpy as np

# 가짜 IMU: 레지스터 0x3B부터 가속도 x, y, z가 2바이트씩, 큰 자리 먼저, 2의 보수로 들어 있다.
# 주소와 배치는 이 예제를 위해 정한 것이다. 실제 칩은 데이터시트의 레지스터 표를 따른다
_감도 = 16384                                      # ±2g를 16비트에 담으면 1g = 32768 / 2
_기울기 = np.deg2rad([20.0, -10.0])                  # 칩이 실제로 기운 각도(롤, 피치)
_참_가속도 = np.array([-np.sin(_기울기[1]),
                     np.sin(_기울기[0]) * np.cos(_기울기[1]),
                     np.cos(_기울기[0]) * np.cos(_기울기[1])])   # 가만히 있으면 중력만 잰다(g)
_메모리 = bytearray(0x80)
for i, 값 in enumerate(np.round(_참_가속도 * _감도).astype(int)):
    _메모리[0x3B + 2 * i:0x3D + 2 * i] = int(값).to_bytes(2, "big", signed=True)


def 레지스터_읽기(시작: int, 개수: int) -> bytes:
    """I2C의 '이 주소부터 몇 바이트 읽기'를 흉내 낸다."""
    return bytes(_메모리[시작:시작 + 개수])


원본 = 레지스터_읽기(0x3B, 6)
print("받은 바이트:", 원본.hex(" "))
가속도 = np.array([int.from_bytes(원본[i:i + 2], "big", signed=True) for i in (0, 2, 4)]) / _감도
print("가속도(g):", np.round(가속도, 4))

# 가만히 있을 때는 중력 방향으로 기울기를 알 수 있다(8장에서 자이로와 합친다)
롤 = np.arctan2(가속도[1], 가속도[2])
피치 = np.arctan2(-가속도[0], np.hypot(가속도[1], 가속도[2]))
print(f"롤 {np.rad2deg(롤):.2f}도, 피치 {np.rad2deg(피치):.2f}도")
