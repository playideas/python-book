"""18장: 15장의 집고 놓기 장면을 '관측을 보고 행동 하나를 고르는' 걸음 단위 환경으로."""
import mujoco
import numpy as np

from 팔집게장면 import 받침_위치, 상자_반크기, 장면_xml, 준비

제어_주기 = 0.02                        # 50Hz로 행동을 고른다
최대_걸음 = 400                         # 한 에피소드는 8초
높이 = 받침_위치[2] + 상자_반크기[2]      # 탁자 위에 놓인 상자 가운데 높이
놓을_곳 = np.array([0.3, -0.25])
상자_범위 = ([0.3, -0.05], [0.5, 0.25])   # 상자가 놓이는 탁자 위 x, y 범위(m)
열림, 닫힘 = 0.08, 0.0                  # 집게 너비 명령(m)
최대_변화 = 0.1                          # 한 걸음에 관절 목표를 바꿀 수 있는 최대값(rad). 안전 장치


class 집고놓기환경:
    def __init__(self, 상자_위치, 흔들림: float = 0.0, 씨앗: int = 0) -> None:
        self.모델 = mujoco.MjModel.from_xml_string(장면_xml(상자_위치, 0.0, 놓을_곳))
        self.데이터 = mujoco.MjData(self.모델)
        준비(self.모델, self.데이터)
        self.걸음 = 0
        self.흔들림, self.생성기 = 흔들림, np.random.default_rng(씨앗)   # 관절 명령에 섞이는 잡음(rad)
        self.하위_걸음 = int(round(제어_주기 / self.모델.opt.timestep))

    def 관측(self) -> np.ndarray:
        """관절 각도 6개, 집게 너비, 상자 위치 3개, TCP에서 본 상자 3개를 이은 13개짜리 벡터."""
        d = self.데이터
        상자 = d.body("box").xpos
        return np.concatenate([d.qpos[:6], d.sensor("width").data, 상자, 상자 - d.site("tcp").xpos])

    def 한걸음(self, 행동) -> None:
        """행동 = [관절 6개를 얼마나 더 돌릴지(rad), 집게 너비 명령(m)]."""
        변화 = np.clip(행동[:6], -최대_변화, 최대_변화)
        self.데이터.ctrl[:6] = self.데이터.qpos[:6] + 변화 + self.생성기.normal(0, self.흔들림, 6)
        self.데이터.ctrl[6] = 열림 if 행동[6] > (열림 + 닫힘) / 2 else 닫힘   # 집게는 열기·닫기 둘 중 하나
        for _ in range(self.하위_걸음):
            mujoco.mj_step(self.모델, self.데이터)
        self.걸음 += 1

    def 잡고_있나(self) -> bool:
        d = self.데이터
        닿음 = min(d.sensor("touch_l").data[0], d.sensor("touch_r").data[0])
        return 닿음 > 1.0 and d.sensor("width").data[0] > 0.01

    def 성공(self) -> bool:
        """상자가 놓을 곳 3cm 안, 탁자 위에 있고, 집게가 열려 있다."""
        상자 = self.데이터.body("box").xpos
        return (np.linalg.norm(상자[:2] - 놓을_곳) < 0.03 and 상자[2] < 높이 + 0.005
                and self.데이터.sensor("width").data[0] > 0.06)

    def 끝났나(self) -> bool:
        """성공한 뒤 집게가 상자 위로 물러났으면 에피소드를 끝낸다."""
        return self.성공() and self.데이터.site("tcp").xpos[2] > 높이 + 0.07

    def 망쳤나(self) -> bool:
        """상자가 탁자 밖으로 떨어졌으면 더 해 볼 것이 없다."""
        return self.데이터.body("box").xpos[2] < 받침_위치[2]
