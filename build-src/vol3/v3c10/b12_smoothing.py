import matplotlib.pyplot as plt
import numpy as np

from 골격도구 import 번호
from 손흔들기데이터 import 시간, 참_키포인트, 초당_프레임

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

생성기 = np.random.default_rng(0)
참값들 = {이름: 참_키포인트()[:, 번호[이름], 1] for 이름 in ["왼손목", "오른손목"]}    # 좌우(y) 위치(m)
잰값들 = {이름: 값 + 생성기.normal(0, 0.015, len(값)) for 이름, 값 in 참값들.items()}  # 1.5cm 떨림


def 이동_평균(값들: np.ndarray, 창: int) -> np.ndarray:
    """지금까지 들어온 최근 '창'개의 평균. 앞으로 올 값은 쓰지 않는다."""
    return np.array([값들[max(0, k - 창 + 1):k + 1].mean() for k in range(len(값들))])


def 저역통과(값들: np.ndarray, 알파: float) -> np.ndarray:
    """1차 저역통과: 새 값 쪽으로 알파만큼만 다가간다."""
    결과 = [값들[0]]
    for 값 in 값들[1:]:
        결과.append(결과[-1] + 알파 * (값 - 결과[-1]))
    return np.array(결과)


def 오차_mm(걸러진: np.ndarray, 참값: np.ndarray) -> float:
    return float(np.sqrt(np.mean((걸러진 - 참값) ** 2)) * 1000)


def 늦음_ms(걸러진: np.ndarray, 참값: np.ndarray) -> float:
    """몇 프레임 늦춰 겹쳤을 때 참값과 가장 잘 맞는지."""
    밀기 = min(range(8), key=lambda k: np.mean((걸러진[k:] - 참값[:len(참값) - k]) ** 2))
    return 밀기 * 1000 / 초당_프레임


거르개들 = {"걸러내기 전": lambda x: x,
         "이동 평균 창 3": lambda x: 이동_평균(x, 3), "이동 평균 창 9": lambda x: 이동_평균(x, 9),
         "저역통과 알파 0.5": lambda x: 저역통과(x, 0.5), "저역통과 알파 0.15": lambda x: 저역통과(x, 0.15)}
print("RMS 오차(mm): 가만히 있는 왼손목 / 흔드는 오른손목, 흔드는 손에서 잰 늦음")
for 이름, 거르개 in 거르개들.items():
    왼, 오른 = (거르개(잰값들[k]) for k in ["왼손목", "오른손목"])
    print(f"  {오차_mm(왼, 참값들['왼손목']):5.1f} / {오차_mm(오른, 참값들['오른손목']):5.1f}, "
          f"늦음 {늦음_ms(오른, 참값들['오른손목']):5.1f}ms  {이름}")

그림, 칸들 = plt.subplots(1, 2, figsize=(8, 3.3))
구간 = 시간 < 2
for 칸, 이름 in zip(칸들, ["왼손목", "오른손목"]):
    칸.plot(시간[구간], 잰값들[이름][구간], ".", color="lightgray", label="측정")
    칸.plot(시간[구간], 참값들[이름][구간], "k-", linewidth=2, label="참값")
    칸.plot(시간[구간], 이동_평균(잰값들[이름], 9)[구간], label="이동 평균 (창 9)")
    칸.plot(시간[구간], 저역통과(잰값들[이름], 0.5)[구간], label="저역통과 (알파 0.5)")
    칸.set(title=f"{이름} ({'가만히' if 이름 == '왼손목' else '흔드는 중'})", xlabel="시간 (초)")
칸들[0].set_ylabel("좌우 위치 y (m)")
그림.legend(*칸들[0].get_legend_handles_labels(), loc="lower center", ncol=4, fontsize=8)
그림.tight_layout(rect=(0, 0.08, 1, 1))
그림.savefig("smoothing.png", dpi=200)
print("저장: smoothing.png")
