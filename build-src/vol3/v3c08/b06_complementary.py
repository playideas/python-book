import matplotlib.pyplot as plt
import numpy as np

from 흔들판 import rms_도, 가속도_피치, 기록하기, 센서_더하기, 주기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def 상보_필터(자이로: np.ndarray, 가속도_피치값: np.ndarray, 알파: float) -> np.ndarray:
    """자이로로 한 걸음 예측하고, 가속도계 쪽으로 (1 - 알파)만큼 끌어당긴다."""
    피치 = 가속도_피치값[0]                       # 처음 값은 가속도계로 잡는다
    결과 = []
    for w, a in zip(자이로, 가속도_피치값):
        피치 = 알파 * (피치 + w * 주기) + (1 - 알파) * a
        결과.append(피치)
    return np.array(결과)


기록 = 기록하기()
자이로, 가속도 = 센서_더하기(기록, np.random.default_rng(0))
참값, 시간 = 기록["참_피치"], 기록["시간"]
추정들 = {
    "자이로만": np.cumsum(자이로) * 주기,
    "가속도계만": 가속도_피치(가속도),
    "상보 필터(알파 0.98)": 상보_필터(자이로, 가속도_피치(가속도), 0.98),
}
for 이름, 추정 in 추정들.items():
    print(f"{이름:14s}: 오차 RMS {rms_도(추정 - 참값):5.2f}도, 가장 클 때 {np.rad2deg(np.abs(추정 - 참값).max()):5.2f}도")

그림, 칸들 = plt.subplots(1, 2, figsize=(10, 3.4), gridspec_kw={"width_ratios": [2, 1]})
for 칸, (시작, 끝) in zip(칸들, [(0, 30), (11, 17)]):
    구간 = (시간 >= 시작) & (시간 <= 끝)
    칸.plot(시간[구간], np.rad2deg(참값[구간]), color="black", lw=2, label="참값")
    for (이름, 추정), 색 in zip(추정들.items(), ["tab:orange", "tab:blue", "tab:red"]):
        칸.plot(시간[구간], np.rad2deg(추정[구간]), color=색, lw=0.8 if 이름 == "가속도계만" else 1.4, label=이름)
    칸.set_xlabel("시간(초)")
    칸.set_ylabel("피치(도)")
칸들[0].legend(fontsize=8, loc="upper left")
칸들[1].set_title("12~16초: 덜덜 떠는 구간", fontsize=10)
그림.tight_layout()
그림.savefig("complementary.png", dpi=200)
print("저장: complementary.png")
