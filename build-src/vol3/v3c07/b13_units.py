import numpy as np

한바퀴 = 4096                 # STS3215의 한 바퀴 눈금 수(12비트 엔코더)
가운데 = 2047                 # 보정 뒤 관절 한가운데가 될 눈금


def 라디안_눈금(각도_rad: float, 방향: int = 1) -> int:
    return round(가운데 + 방향 * 각도_rad * 한바퀴 / (2 * np.pi))


def 눈금_라디안(눈금: int, 방향: int = 1) -> float:
    return 방향 * (눈금 - 가운데) * 2 * np.pi / 한바퀴


print(f"눈금 하나 = {360 / 한바퀴:.4f}도")
for 각도_도 in [-90, 0, 30, 90]:
    눈금 = 라디안_눈금(np.deg2rad(각도_도))
    되돌림 = np.rad2deg(눈금_라디안(눈금))
    print(f"{각도_도:4d}도 → 눈금 {눈금:4d} → {되돌림:8.3f}도")
print("방향이 반대인 관절의 30도 →", 라디안_눈금(np.deg2rad(30), 방향=-1))

# 반올림 때문에 생기는 오차는 눈금 반 개를 넘지 않는다
각도들 = np.deg2rad(np.linspace(-90, 90, 10001))
오차_도 = np.rad2deg([abs(눈금_라디안(라디안_눈금(a)) - a) for a in 각도들])
print(f"가장 큰 반올림 오차: {오차_도.max():.4f}도")
