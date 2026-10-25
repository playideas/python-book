import matplotlib.pyplot as plt
import mujoco
import numpy as np

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# 바닥에 가만히 놓인 상자의 IMU. 자이로에 noise="0.01"을 적어 두었다
xml = """
<mujoco>
  <worldbody>
    <geom type="plane" size="1 1 0.1"/>
    <body pos="0 0 0.05"><freejoint/><geom type="box" size="0.1 0.1 0.05"/><site name="imu"/></body>
  </worldbody>
  <sensor><gyro name="자이로" site="imu" noise="0.01"/></sensor>
</mujoco>
"""
모델 = mujoco.MjModel.from_xml_string(xml)
데이터 = mujoco.MjData(모델)
읽기 = []
for _ in range(10000):
    mujoco.mj_step(모델, 데이터)
    읽기.append(데이터.sensor("자이로").data[1])
읽기 = np.array(읽기)
print(f"MJCF의 noise {모델.sensor_noise[0]} → MuJoCo 자이로 10000번의 표준편차 {읽기.std():.6f}")

# 잡음과 치우침은 직접 더한다(값싼 IMU를 흉내 낸 값, rad/s)
잰_값 = 읽기 + 0.02 + np.random.default_rng(0).normal(0, 0.01, len(읽기))
평균, 표준편차 = 잰_값.mean(), 잰_값.std()
print(f"더한 뒤: 평균 {평균:.4f}, 표준편차 {표준편차:.4f}")
for k in [1, 2, 3]:
    print(f"평균 ±{k}σ 안에 든 비율: {np.mean(np.abs(잰_값 - 평균) < k * 표준편차):.1%}")

그림, 칸 = plt.subplots(figsize=(7, 3))
칸.hist(잰_값, bins=60, density=True, alpha=0.6, label="읽은 값의 분포")
x = np.linspace(평균 - 4 * 표준편차, 평균 + 4 * 표준편차, 200)
칸.plot(x, np.exp(-0.5 * ((x - 평균) / 표준편차) ** 2) / (표준편차 * np.sqrt(2 * np.pi)), "k", label="정규분포 곡선")
칸.axvline(0, color="tab:green", ls="--", label="참값 0")
칸.axvline(평균, color="tab:red", label=f"평균 {평균:.4f}")
칸.set_xlabel("자이로 값(rad/s)")
칸.set_ylabel("밀도")
칸.legend(fontsize=8)
그림.tight_layout()
그림.savefig("gyro_hist.png", dpi=200)
print("저장: gyro_hist.png")
