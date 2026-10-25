import numpy as np

주기, 늦음 = 0.02, 0.1                     # 50Hz, 측정이 0.1초 늦게 도착한다(1장 1.4절의 점 로봇)
늦은_박자 = round(늦음 / 주기)


def 달리기(kp: float, ki: float, kd: float, 초: float = 10.0, 바람: float = -0.2) -> np.ndarray:
    """1m 앞 목표로 가는 1차원 점 로봇. 바람이 늘 -0.2m/s로 민다. 위치 기록을 돌려준다."""
    기록, 적분, 이전_오차 = [0.0], 0.0, None
    for _ in range(round(초 / 주기)):
        오차 = 1.0 - 기록[max(len(기록) - 1 - 늦은_박자, 0)]   # 늦게 도착한 측정으로 판단
        적분 += 오차 * 주기
        미분 = 0.0 if 이전_오차 is None else (오차 - 이전_오차) / 주기
        이전_오차 = 오차
        속도 = kp * 오차 + ki * 적분 + kd * 미분
        기록.append(기록[-1] + (속도 + 바람) * 주기)
    return np.array(기록)


def 커지는_비율(kp: float) -> float:
    """P만으로 달렸을 때 뒤쪽 흔들림 폭 ÷ 앞쪽 흔들림 폭. 1이면 꼭 같은 폭으로 계속 흔들린다."""
    x = 달리기(kp, 0, 0, 초=20, 바람=0.0)
    n = len(x)
    return np.ptp(x[3 * n // 4:]) / np.ptp(x[n // 4:n // 2])


# 1단계: P 이득을 키워 가며 흔들림이 줄지도 커지지도 않는 '한계 이득' Ku를 찾는다(이분 탐색)
아래, 위 = 1.0, 40.0
for _ in range(40):
    가운데 = (아래 + 위) / 2
    아래, 위 = (아래, 가운데) if 커지는_비율(가운데) > 1 else (가운데, 위)
Ku = (아래 + 위) / 2
x = 달리기(Ku, 0, 0, 초=20, 바람=0.0)
올라가며_지남 = np.flatnonzero(np.diff(np.sign(x[500:] - 1.0)) > 0)   # 목표를 아래에서 위로 지나는 박자
Tu = np.mean(np.diff(올라가며_지남)) * 주기
print(f"한계 이득 Ku = {Ku:.2f}, 흔들림 주기 Tu = {Tu:.2f}초")

# 2단계: 지글러-니콜스 표에 넣는다
처방 = {"P": (0.5 * Ku, 0, 0), "PI": (0.45 * Ku, 0.54 * Ku / Tu, 0),
        "PID": (0.6 * Ku, 1.2 * Ku / Tu, 0.075 * Ku * Tu)}
for 이름, (kp, ki, kd) in 처방.items():
    x = 달리기(kp, ki, kd)
    밖 = np.abs(x - 1.0) > 0.02
    정착 = f"{(np.flatnonzero(밖)[-1] + 1) * 주기:.2f}초" if not 밖[-1] else "  못 함"
    print(f"{이름:3s}: kp={kp:5.2f} ki={ki:5.2f} kd={kd:4.2f} → 가장 멀리 {x.max():.3f}m, "
          f"끝 {x[-1]:.3f}m, ±2cm 정착 {정착}")
