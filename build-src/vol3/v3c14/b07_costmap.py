import matplotlib.pyplot as plt
import numpy as np

from 주행장면 import 장면_만들기
from 지도도구 import 내접, 비용_지도, 지도_그리기, 지도_원점, 지도_크기, 치명, 해상도

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

모델, _ = 장면_만들기()
찬칸 = 지도_그리기(모델)
비용 = 비용_지도(찬칸)
print("지도 크기:", 지도_크기, "칸 /", 해상도, "m 간격")
print(f"치명(254) {np.sum(비용 == 치명)}칸, 내접(253) {np.sum(비용 == 내접)}칸, "
      f"부풀림(1~252) {np.sum((비용 > 0) & (비용 < 내접))}칸, 빈칸(0) {np.sum(비용 == 0)}칸")
# y = 2.5m 줄에서 왼쪽 벽의 마지막 찬칸부터 방 안쪽으로 두 칸씩 건너뛰며 비용을 읽는다
j = int((2.5 - 지도_원점[1]) / 해상도)
벽_끝 = np.nonzero(찬칸[:40, j])[0].max()
print("벽 칸에서 떨어진 거리(m):", [round(k * 해상도, 2) for k in range(0, 14, 2)])
print("비용                :", [int(비용[벽_끝 + k, j]) for k in range(0, 14, 2)])

범위 = [지도_원점[0], 지도_원점[0] + 지도_크기[0] * 해상도, 지도_원점[1], 지도_원점[1] + 지도_크기[1] * 해상도]
그림, 칸 = plt.subplots(figsize=(6.4, 4.4))
면 = 칸.imshow(비용.T, origin="lower", extent=범위, cmap="magma_r")
그림.colorbar(면, ax=칸, shrink=0.8, label="비용")
칸.set(title="비용 지도(로봇 반지름 0.2m, 부풀림 0.55m)", xlabel="x(m)", ylabel="y(m)")
그림.tight_layout()
그림.savefig("costmap.png", dpi=200)
print("저장: costmap.png")
