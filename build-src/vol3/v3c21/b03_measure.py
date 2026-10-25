import matplotlib.pyplot as plt
import mujoco
import numpy as np
from matplotlib.patches import Circle, Rectangle

from 책상인지 import 물건_찾기
from 책상장면 import 대기_자세, 무작위_배치, 상자_안쪽, 상자들, 연필꽂이, 장면_xml, 종류들, 찍기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

물건들 = 무작위_배치(np.random.default_rng(18), {"빨강": 2, "초록": 2, "파랑": 1})
모델 = mujoco.MjModel.from_xml_string(장면_xml(물건들))
데이터 = mujoco.MjData(모델)
데이터.qpos[:6] = 데이터.ctrl[:6] = 대기_자세
mujoco.mj_forward(모델, 데이터)
잰_것들 = 물건_찾기(*찍기(모델, 데이터))


def 직사각형(중심, 요_도, 길이, 폭, **모양) -> Rectangle:
    """가운데·요·크기로 위에서 본 직사각형을 만든다."""
    ψ = np.deg2rad(요_도)
    구석 = np.asarray(중심[:2]) - np.array([[np.cos(ψ), -np.sin(ψ)], [np.sin(ψ), np.cos(ψ)]]) @ [길이 / 2, 폭 / 2]
    return Rectangle(구석, 길이, 폭, angle=요_도, **모양)


그림, 칸 = plt.subplots(figsize=(6.4, 5.2))
for 물건 in 물건들:
    반 = 종류들[물건["종류"]][0]
    칸.add_patch(직사각형(물건["위치"], 물건["요"], 2 * 반[0], 2 * 반[1], color="lightgray"))
for 잰 in 잰_것들:
    참 = min(물건들, key=lambda 물건: np.linalg.norm(물건["위치"] - 잰["중심"][:2]))
    요_차이 = (잰["요_도"] - 참["요"] + 90) % 180 - 90                # 상자는 180도 돌려도 같은 모양
    print(f"{잰['종류']}: 가운데 ({잰['중심'][0]:.3f}, {잰['중심'][1]:.3f}, {잰['중심'][2]:.3f}) "
          f"오차 {np.linalg.norm(잰['중심'][:2] - 참['위치']) * 1000:3.1f}mm, 요 오차 {요_차이:5.1f}도, "
          f"크기 {잰['길이'] * 100:.1f}×{잰['폭'] * 100:.1f}×{잰['높이'] * 100:.1f}cm, 자리 {잰['자리']}")
    칸.add_patch(직사각형(잰["중심"], 잰["요_도"], 잰["길이"], 잰["폭"], fill=False,
                       edgecolor={"빨강": "red", "초록": "green", "파랑": "blue"}[잰["종류"]], linewidth=1.5))
for 종류, 곳 in 상자들.items():
    칸.add_patch(Rectangle(곳 - 상자_안쪽, 2 * 상자_안쪽, 2 * 상자_안쪽, fill=False, edgecolor="k", linestyle="--"))
    칸.text(곳[0], 곳[1], f"{종류} 상자", ha="center", va="center", fontsize=9)
칸.add_patch(Circle(연필꽂이[0], 연필꽂이[1], color="dimgray"))
칸.plot(0, 0, "ks")
칸.text(0.0, -0.035, "받침", ha="center", fontsize=9)
칸.set(xlim=(-0.05, 0.65), ylim=(-0.42, 0.33), aspect="equal", xlabel="x (m)", ylabel="y (m)")
칸.set_title("위에서 본 책상: 회색은 참값, 색 테두리는 잰 값", fontsize=10)
그림.tight_layout()
그림.savefig("measured_map.png", dpi=200)
print("저장: measured_map.png")
