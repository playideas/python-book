import matplotlib.pyplot as plt
import mujoco

from 지시수행 import 이름표
from 지시장면 import 장면_xml, 찍기
from 찾기도구 import 개방어휘검출기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

모델 = mujoco.MjModel.from_xml_string(장면_xml())
데이터 = mujoco.MjData(모델)
사진, _ = 찍기(모델, 데이터)
검출기 = 개방어휘검출기()
print(f"매개변수 {sum(p.numel() for p in 검출기.모델.parameters()):,}개")

찾은것 = 검출기.찾기(사진, list(이름표.values()))
그림, 칸 = plt.subplots(figsize=(6.4, 4.8))
칸.imshow(사진)
for 이름, 글 in 이름표.items():
    점수, (x1, y1, x2, y2) = 찾은것[글]
    print(f"{글:13s} → 점수 {점수:.2f}, 상자 x {x1:.0f}~{x2:.0f}, y {y1:.0f}~{y2:.0f}")
    칸.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, color="white", lw=1.5))
    칸.text(x2 + 4, y1, f"{이름} {점수:.2f}", color="white", fontsize=8, va="top", backgroundcolor="black")
칸.axis("off")
그림.tight_layout()
그림.savefig("owl.png", dpi=200)
print("저장: owl.png")
