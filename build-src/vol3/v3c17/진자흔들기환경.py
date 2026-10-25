"""17장: 16장의 진자 흔들어 올리기를 Gymnasium 환경으로 감싼 것."""
from collections.abc import Callable

import gymnasium as gym
import mujoco
import numpy as np

from 진자장면 import 세운_자세_오차, 장면, 토크_한계


class 진자흔들기환경(gym.Env):
    """관측 [cos θ, sin θ, 각속도], 행동 -1~1(토크 한계에 곱함), 보상은 16장 MPPI 비용에 음수를 붙인 것."""

    metadata = {"render_modes": ["rgb_array"], "render_fps": 100}

    def __init__(self, 최대_걸음: int = 600, 보상_함수: Callable[[float, float, float], float] | None = None,
                 render_mode: str | None = None):
        self.모델, self.데이터 = 장면()
        self.최대_걸음 = 최대_걸음
        self.보상_함수 = 보상_함수 or MPPI_비용_보상
        self.render_mode = render_mode
        self.observation_space = gym.spaces.Box(-np.inf, np.inf, shape=(3,), dtype=np.float32)
        self.action_space = gym.spaces.Box(-1.0, 1.0, shape=(1,), dtype=np.float32)
        self.렌더러 = None

    def _관측(self) -> np.ndarray:
        각도, 각속도 = self.데이터.qpos[0], self.데이터.qvel[0]
        return np.array([np.cos(각도), np.sin(각도), 각속도], dtype=np.float32)

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)                                  # self.np_random을 씨앗으로 맞춘다
        mujoco.mj_resetData(self.모델, self.데이터)
        self.데이터.qpos[0] = self.np_random.uniform(-0.1, 0.1)    # 매달린 자세 근처에서 조금씩 다르게
        self.데이터.qvel[0] = self.np_random.uniform(-0.1, 0.1)
        mujoco.mj_forward(self.모델, self.데이터)
        self.걸음 = 0
        return self._관측(), {}

    def step(self, 행동: np.ndarray):
        토크 = float(np.clip(행동[0], -1.0, 1.0)) * 토크_한계
        self.데이터.ctrl[0] = 토크
        mujoco.mj_step(self.모델, self.데이터)
        self.걸음 += 1
        각도, 각속도 = self.데이터.qpos[0], self.데이터.qvel[0]
        보상 = self.보상_함수(각도, 각속도, 토크)
        잘림 = self.걸음 >= self.최대_걸음                       # 쓰러져 끝나는 일은 없고, 시간만 자른다
        return self._관측(), 보상, False, 잘림, {"오차_도": np.rad2deg(abs(세운_자세_오차(각도)))}

    def render(self) -> np.ndarray:
        if self.렌더러 is None:
            self.렌더러 = mujoco.Renderer(self.모델, 240, 240)
        self.렌더러.update_scene(self.데이터, camera="옆")
        return self.렌더러.render()

    def close(self) -> None:
        if self.렌더러 is not None:
            self.렌더러.close()
            self.렌더러 = None


def MPPI_비용_보상(각도: float, 각속도: float, 토크: float) -> float:
    """16장 MPPI의 한 걸음 비용(자세 오차² + 0.1·각속도² + 0.01·토크²)에 음수를 붙인 보상."""
    return -float(세운_자세_오차(각도) ** 2 + 0.1 * 각속도 ** 2 + 0.01 * 토크 ** 2)
