import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

시간_ms = np.arange(0, 60, 0.01)                   # 60ms 동안
그림, 칸들 = plt.subplots(3, 1, figsize=(7, 4.2), sharex=True)
for 칸, (각도, 폭) in zip(칸들, [(0, 1.0), (90, 1.5), (180, 2.0)]):
    신호 = (시간_ms % 20.0) < 폭                   # 20ms마다 '폭'만큼만 켜진다
    칸.plot(시간_ms, 신호 * 5.0, color="tab:blue")
    칸.set_ylim(-0.8, 6.2)
    칸.set_yticks([0, 5])
    칸.set_ylabel("V")
    칸.text(23.0, 3.2, f"폭 {폭}ms → {각도}도", fontsize=9)
칸들[-1].set_xlabel("시간(ms)")
그림.tight_layout()
그림.savefig("pwm_servo.png", dpi=200)
print("저장: pwm_servo.png")
