import mujoco
import numpy as np

from 이중적분기 import A, B, 굴리기, 주기

# 1kg 수레가 마찰 없는 레일(x축 미끄럼 관절) 위에 있고, motor가 밀어 준다(힘 1N = 가속도 1m/s²)
xml = """
<mujoco>
  <option timestep="0.001" gravity="0 0 0"/>
  <worldbody>
    <body name="수레">
      <joint name="레일" type="slide" axis="1 0 0"/>
      <geom type="box" size="0.1 0.05 0.05" mass="1"/>
    </body>
  </worldbody>
  <actuator><motor joint="레일" gear="1"/></actuator>
</mujoco>
"""
모델 = mujoco.MjModel.from_xml_string(xml)
데이터 = mujoco.MjData(모델)
입력들 = np.random.default_rng(0).uniform(-1, 1, size=30)      # 3초 동안 아무렇게나 민다
한_주기_걸음 = round(주기 / 모델.opt.timestep)

시뮬 = [[0.0, 0.0]]
for u in 입력들:
    데이터.ctrl[0] = u                                  # 한 주기 동안 같은 힘을 유지한다
    for _ in range(한_주기_걸음):
        mujoco.mj_step(모델, 데이터)
    시뮬.append([데이터.qpos[0], 데이터.qvel[0]])
시뮬 = np.array(시뮬)

예측 = 굴리기([0.0, 0.0], 입력들)
B_어림 = np.array([[0.0], [주기]])                      # Δt²/2 항을 빼먹은 어림
어림 = [np.zeros(2)]
for u in 입력들:
    어림.append(A @ 어림[-1] + B_어림[:, 0] * u)
어림 = np.array(어림)
print(f"3초 뒤 MuJoCo 위치 {시뮬[-1, 0]:.4f}m, A·B 예측 {예측[-1, 0]:.4f}m, 어림 {어림[-1, 0]:.4f}m")
print(f"가장 큰 위치 차이: A·B 예측 {np.abs(시뮬 - 예측)[:, 0].max() * 1000:.2f}mm, "
      f"어림 {np.abs(시뮬 - 어림)[:, 0].max() * 1000:.2f}mm")
