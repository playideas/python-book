import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# 용수철에 매달린 1kg 추: 가속도 = -k·위치. 처음 위치 0.1m, 정지. 정답은 0.1·cos(ω t)
k = 100.0                                     # N/m, ω = 10rad/s (주기 약 0.63초)
ω = np.sqrt(k)


def 흘리기(방법: str, 간격: float, 시간: float = 3.0) -> tuple[np.ndarray, np.ndarray]:
    x, v = 0.1, 0.0
    시각들, 위치들 = [0.0], [x]
    for i in range(int(round(시간 / 간격))):
        a = -k * x
        if 방법 == "오일러":                  # 옛 속도로 위치를 옮긴다
            x, v = x + v * 간격, v + a * 간격
        else:                                  # 반암시적 오일러: 속도 먼저, 새 속도로 위치(MuJoCo 기본)
            v = v + a * 간격
            x = x + v * 간격
        시각들.append((i + 1) * 간격)
        위치들.append(x)
    return np.array(시각들), np.array(위치들)


그림, 칸 = plt.subplots(figsize=(6.4, 3.0))
t = np.linspace(0, 3, 600)
칸.plot(t, 0.1 * np.cos(ω * t), color="black", linewidth=1, label="정답")
for 방법, 간격, 색 in [("오일러", 0.01, "tab:red"), ("반암시적 오일러", 0.01, "tab:blue")]:
    시각, 위치 = 흘리기(방법, 간격)
    오차 = np.max(np.abs(위치 - 0.1 * np.cos(ω * 시각)))
    print(f"{방법:8s} 간격 {간격}초: 3초 동안 최대 진폭 {np.max(np.abs(위치)):.3f}m, 정답과 최대 차이 {오차:.4f}m")
    칸.plot(시각, 위치, color=색, linewidth=1.2, label=f"{방법} (간격 {간격}초)")
for 간격 in [0.15, 0.25]:                     # 안정 한계 2/ω = 0.2초 근처
    _, 위치 = 흘리기("반암시적 오일러", 간격)
    print(f"반암시적 오일러 간격 {간격}초: 3초 동안 최대 진폭 {np.max(np.abs(위치)):.3g}m")
칸.set_xlabel("시간(초)")
칸.set_ylabel("위치(m)")
칸.set_ylim(-0.5, 0.5)
칸.legend(loc="upper left", fontsize=8, ncol=3)
그림.tight_layout()
그림.savefig("integrators.png", dpi=200)
print("저장: integrators.png")
