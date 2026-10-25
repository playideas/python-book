"""13장 실습: 목표 자세를 시각마다 position 액추에이터에 넣으며 시뮬레이션하고 기록한다."""
import mujoco
import numpy as np

from 실습장면 import XML, 기둥들, 시작_자세


def 실행(목표_함수, 시간: float) -> dict[str, np.ndarray]:
    """목표_함수(t) → 그 시각의 관절 목표. 시각, 관절, 목표, 손끝, 팔-기둥 접촉 수, 팔-기둥 거리를 기록한다."""
    모델 = mujoco.MjModel.from_xml_string(XML())
    데이터 = mujoco.MjData(모델)
    데이터.qpos[:] = 시작_자세
    mujoco.mj_forward(모델, 데이터)
    팔 = {모델.geom(f"arm{i}").id for i in (1, 2, 3)}
    기둥 = {모델.geom(f"pillar{i}").id for i in range(len(기둥들))}
    기록 = {"시각": [], "관절": [], "목표": [], "손끝": [], "접촉": [], "거리": []}
    while 데이터.time < 시간 - 1e-9:
        데이터.ctrl[:] = 목표_함수(데이터.time)
        mujoco.mj_step(모델, 데이터)
        mujoco.mj_forward(모델, 데이터)                    # 접촉·위치를 지금 상태로 맞춘다
        짝들 = [{c.geom1, c.geom2} for c in 데이터.contact[:데이터.ncon]]
        기록["시각"].append(데이터.time)
        기록["관절"].append(데이터.qpos.copy())
        기록["목표"].append(데이터.ctrl.copy())
        기록["손끝"].append(데이터.site("tip").xpos[:2].copy())
        기록["접촉"].append(sum(1 for 짝 in 짝들 if 짝 & 팔 and 짝 & 기둥))
        기록["거리"].append(min(mujoco.mj_geomDistance(모델, 데이터, a, b, 1.0, None) for a in 팔 for b in 기둥))
    return {k: np.array(v) for k, v in 기록.items()}
