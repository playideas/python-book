import matplotlib.pyplot as plt
import mujoco
import numpy as np
from matplotlib.patches import Circle, Rectangle

from 작업판단 import 빈_칸
from 정리로봇 import 계획하는_집고놓기
from 집고놓기 import 단계, 집고놓기
from 책상인지 import 물건_찾기, 어느_상자
from 책상장면 import 대기_자세, 무작위_배치, 상자_안쪽, 상자들, 연필꽂이, 장면_xml, 찍기

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


class 곧게_옮기기(계획하는_집고놓기):
    """비교용: 옮기기만 15장처럼 손끝 직선으로 간다."""
    def 길(self, 곳, 위로, 요_도, 시간):
        if self.단계 is 단계.옮기기:
            return 집고놓기.길(self, 곳, 위로, 요_도, 시간)
        return super().길(곳, 위로, 요_도, 시간)


물건들 = 무작위_배치(np.random.default_rng(0), {"빨강": 2, "초록": 2, "파랑": 1})
그림, 칸 = plt.subplots(figsize=(6.4, 5.2))
for 방법, 작업_종류, 색 in [("손끝 직선", 곧게_옮기기, "tab:red"), ("계획한 경로", 계획하는_집고놓기, "tab:blue")]:
    모델 = mujoco.MjModel.from_xml_string(장면_xml(물건들))
    데이터 = mujoco.MjData(모델)
    데이터.qpos[:6] = 데이터.ctrl[:6] = 대기_자세
    데이터.ctrl[6] = 0.08
    mujoco.mj_forward(모델, 데이터)
    잰_것들 = 물건_찾기(*찍기(모델, 데이터))
    대상 = min((잰 for 잰 in 잰_것들 if 잰["종류"] == "빨강"), key=lambda 잰: 잰["중심"][1])   # 연필꽂이 쪽 빨강
    펜, 닿은_걸음, 손끝 = 모델.geom("연필꽂이").id, [0], []

    def 지켜보기(작업) -> None:
        닿은_걸음[0] += any(펜 in (c.geom1, c.geom2) for c in 데이터.contact[:데이터.ncon])
        손끝.append(데이터.site("tcp").xpos[:2].copy())

    작업 = 작업_종류(모델, 데이터, 대상, [잰 for 잰 in 잰_것들 if 잰 is not 대상],
                 [*빈_칸("빨강", 잰_것들), 대상["중심"][2]], np.random.default_rng(0))
    작업.실행(최대_시간=30, 찍기=지켜보기)
    빨강 = 데이터.body("빨강0").xpos                                   # 대상의 참값 몸체
    print(f"[{방법}] {' → '.join(단계 + (f'({메모})' if 메모 else '') for _, 단계, 메모 in 작업.기록[3:])}")
    print(f"   연필꽂이와 닿은 제어 주기 {닿은_걸음[0]}번, 빨강 블록 ({빨강[0]:.3f}, {빨강[1]:.3f}) 자리 {어느_상자(빨강)}"
          f", 계획(단계, 경유점, 충돌 검사) {작업.계획_기록}")
    칸.plot(*np.array(손끝).T, color=색, label=방법)
for 종류, 곳 in 상자들.items():
    칸.add_patch(Rectangle(곳 - 상자_안쪽, 2 * 상자_안쪽, 2 * 상자_안쪽, fill=False, edgecolor="k", linestyle="--"))
칸.add_patch(Circle(연필꽂이[0], 연필꽂이[1], color="dimgray"))
칸.plot(*대상["중심"][:2], "rs")
칸.set(xlim=(-0.05, 0.65), ylim=(-0.42, 0.33), aspect="equal", xlabel="x (m)", ylabel="y (m)",
      title="위에서 본 손끝(TCP) 경로")
칸.legend(fontsize=9, loc="upper left")
그림.tight_layout()
그림.savefig("straight_vs_plan.png", dpi=200)
print("저장: straight_vs_plan.png")
