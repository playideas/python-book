import matplotlib.pyplot as plt
import numpy as np

from 골격도구 import 번호
from 따라하기 import 사람_팔_각, 오른팔_복원, 저역통과
from 손흔들기데이터 import 시간, 잰_픽셀, 참_키포인트, 카메라들

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# 1) 두 카메라의 픽셀(잡음 2px) → 2) 삼각측량
참_팔 = 참_키포인트()[:, [번호["오른어깨"], 번호["오른팔꿈치"], 번호["오른손목"]]]
복원_팔 = 오른팔_복원(카메라들, 잰_픽셀(잡음_px=2.0))
오차 = np.linalg.norm(복원_팔 - 참_팔, axis=2) * 1000
print("3D 오차 평균(mm) 어깨·팔꿈치·손목:", 오차.mean(axis=0).round(1), "/ 가장 클 때", round(float(오차.max()), 1))

# 3) 관절 각도 → 4) 관절마다 다른 세기로 거르기
참_각 = np.rad2deg([사람_팔_각(*팔) for 팔 in 참_팔])
잰_각 = np.rad2deg([사람_팔_각(*팔) for 팔 in 복원_팔])
for 알파 in [1.0, 0.7, 0.5, 0.3]:
    걸러진 = np.column_stack([저역통과(잰_각[:, j], 알파) for j in range(2)])
    rms = np.sqrt(np.mean((걸러진 - 참_각) ** 2, axis=0))
    print(f"알파 {알파}: 각도 RMS 오차 어깨 {rms[0]:5.2f}도, 팔꿈치 {rms[1]:5.2f}도")
최종_각 = np.column_stack([저역통과(잰_각[:, 0], 0.5), 잰_각[:, 1]])     # 느린 어깨만 거른다

그림, 칸들 = plt.subplots(2, 1, figsize=(7, 4.7), sharex=True)
for j, (칸, 이름) in enumerate(zip(칸들, ["어깨 각", "팔꿈치 각"])):
    칸.plot(시간, 잰_각[:, j], ".", color="lightgray", label="삼각측량 그대로")
    칸.plot(시간, 참_각[:, j], "k-", linewidth=2, label="참값")
    칸.plot(시간, 최종_각[:, j], color="tab:orange", label="거른 뒤(어깨 알파 0.5)")
    칸.set_ylabel(f"{이름} (도)")
칸들[1].set_xlabel("시간 (초)")
그림.legend(*칸들[0].get_legend_handles_labels(), loc="lower center", ncol=3, fontsize=8)
그림.tight_layout(rect=(0, 0.06, 1, 1))
그림.savefig("practice_angles.png", dpi=200)
print("저장: practice_angles.png")
