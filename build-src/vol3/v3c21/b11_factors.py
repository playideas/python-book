from dataclasses import replace

import matplotlib.pyplot as plt

from 책상장면 import 물성
from 평가도구 import 한_판, 현실_물성

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# 20장 20.2절처럼 현실 역할의 차이를 하나씩만 켜서 범인을 찾는다(판 수를 줄여 10판씩)
하나씩 = {"마찰": dict(물건_마찰=현실_물성.물건_마찰, 패드_마찰=현실_물성.패드_마찰),
        "무게 2배": dict(질량_배율=현실_물성.질량_배율), "조명 0.6": dict(밝기=현실_물성.밝기),
        "깊이 잡음": dict(깊이_잡음=현실_물성.깊이_잡음), "카메라 받침": dict(카메라_틀어짐=현실_물성.카메라_틀어짐)}
정리_수, 실패_수 = [], []
for 이름, 바꿀_것 in 하나씩.items():
    판들 = [한_판(씨앗, replace(물성(), **바꿀_것)) for 씨앗 in range(10)]
    정리_수.append(sum(판["정리"] for 판 in 판들))
    실패_수.append(sum(sum(판["원인"].values()) + 판["확인 실패"] for 판 in 판들))
    print(f"{이름:6s}만: 물건 {정리_수[-1]}/40, 실패·확인 실패 {실패_수[-1]}번")

그림, 칸 = plt.subplots(figsize=(7, 3.2))
위치 = range(len(하나씩))
칸.bar([x - 0.2 for x in 위치], 정리_수, width=0.4, label="정리한 물건(40개 중)")
칸.bar([x + 0.2 for x in 위치], 실패_수, width=0.4, label="실패·확인 실패 횟수")
칸.set_xticks(list(위치), list(하나씩))
칸.set_ylim(0, 52)
칸.legend(fontsize=9, loc="upper center", ncol=2)
칸.set_title("현실 역할의 차이를 하나씩 켰을 때(10판)", fontsize=10)
그림.tight_layout()
그림.savefig("factors.png", dpi=200)
print("저장: factors.png")
