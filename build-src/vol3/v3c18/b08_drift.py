import matplotlib.pyplot as plt
import numpy as np

from 모방환경 import 제어_주기
from 시연도구 import 굴리기, 시연_모으기, 시험_위치
from 전문가 import 목표_정하기, 전문가
from 정책도구 import 학습

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

데이터 = 시연_모으기(250)
학습_칸 = 데이터["에피소드"] < 200
정책 = 학습(데이터["관측"][학습_칸], 데이터["행동"][학습_칸])
상자 = 시험_위치(50)[0]

그림, 칸 = plt.subplots(figsize=(7.5, 3.2))
for 이름, 운전자, 색 in [("전문가가 움직일 때", None, "tab:blue"), ("BC 정책이 움직일 때", 정책, "tab:red")]:
    차이, 단계들 = [], []

    def 찍기(환경) -> None:
        """한 걸음 뒤의 상태에서 정책과 전문가에게 같은 질문을 던져 답의 차이를 잰다."""
        차이.append(np.abs(정책(환경.관측())[:6] - 전문가(환경)[:6]).max())
        단계들.append(목표_정하기(환경)[2])

    _, _, 성공 = 굴리기(상자, 운전자, 흔들림=0.004, 씨앗=0, 찍기=찍기)
    시각 = np.arange(1, len(차이) + 1) * 제어_주기
    칸.plot(시각, np.degrees(차이), color=색, linewidth=1, label=f"{이름} ({'성공' if 성공 else '실패'})")
    print(f"{이름}: {len(차이)}걸음, 차이 중앙값 {np.degrees(np.median(차이)):.2f}도, "
          f"가장 클 때 {np.degrees(max(차이)):.1f}도, 마지막 단계 {단계들[-1]}")
칸.set_xlabel("시간 (초)")
칸.set_ylabel("정책과 전문가의 답 차이 (도)")
칸.legend()
그림.tight_layout()
그림.savefig("drift.png", dpi=200)
print("저장: drift.png")
