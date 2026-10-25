"""16장: MuJoCo 모델을 예측기로 쓰는 MPPI(경로 적분 모델 예측 제어). 학습 없이, 굴려 보고 고른다."""
import mujoco
import numpy as np
from mujoco import rollout

from 진자장면 import 세운_자세_오차, 토크_한계


class MPPI:
    def __init__(self, 모델: mujoco.MjModel, 후보_수: int = 128, 걸음_수: int = 100,
                 흔들기: float = 1.0, 온도: float = 1.0, 씨앗: int = 0, 스레드: int = 8):
        self.모델, self.K, self.T = 모델, 후보_수, 걸음_수
        self.흔들기, self.온도 = 흔들기, 온도
        self.생성기 = np.random.default_rng(씨앗)
        self.상상들 = [mujoco.MjData(모델) for _ in range(스레드)]   # 예측 전용 데이터
        self.상태_종류 = mujoco.mjtState.mjSTATE_FULLPHYSICS
        self.지금 = np.empty(mujoco.mj_stateSize(모델, self.상태_종류))
        self.계획 = np.zeros(걸음_수)                                # 지금까지의 최선 입력열(N·m)

    def 비용(self, 상태들: np.ndarray, 입력들: np.ndarray) -> np.ndarray:
        """후보마다 '거꾸로 선 자세에서 먼 정도 + 빠르기 + 힘'을 시간에 걸쳐 더한다."""
        각도, 각속도 = 상태들[:, :, 1], 상태들[:, :, 2]               # 상태 = [시각, qpos, qvel]
        return np.sum(세운_자세_오차(각도)**2 + 0.1 * 각속도**2 + 0.01 * 입력들**2, axis=1)

    def 고르기(self, 진짜: mujoco.MjData) -> float:
        """지금 상태에서 후보를 굴려 보고, 비용이 낮을수록 큰 가중치로 평균 내 계획을 고친다."""
        mujoco.mj_getState(self.모델, 진짜, self.지금, self.상태_종류)
        잡음 = self.생성기.normal(0, self.흔들기, size=(self.K, self.T))
        후보들 = np.clip(self.계획 + 잡음, -토크_한계, 토크_한계)
        상태들, _ = rollout.rollout(self.모델, self.상상들, self.지금, 후보들[:, :, None])
        비용들 = self.비용(상태들, 후보들)
        가중치 = np.exp(-(비용들 - 비용들.min()) / self.온도)        # 가장 좋은 후보가 1
        가중치 /= 가중치.sum()
        self.계획 = 가중치 @ 후보들                                  # 가중 평균이 새 계획
        첫_입력 = float(self.계획[0])
        self.계획 = np.r_[self.계획[1:], self.계획[-1]]              # 다음 주기를 위해 한 칸 당긴다
        return 첫_입력
