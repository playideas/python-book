"""16장: 직선 위를 미끄러지는 1kg 수레(이중 적분기). 상태는 [위치(m), 속도(m/s)], 입력은 가속도(m/s²)."""
import numpy as np

주기 = 0.1                                   # 제어 주기(초): 10Hz로 판단한다

# 한 주기 동안 같은 가속도 u를 낼 때: 위치 += 속도·Δt + u·Δt²/2, 속도 += u·Δt
A = np.array([[1.0, 주기],
              [0.0, 1.0]])
B = np.array([[주기**2 / 2],
              [주기]])


def 굴리기(x0: np.ndarray, 입력들: np.ndarray) -> np.ndarray:
    """처음 상태에서 입력을 차례로 넣어 상태 기록((N+1)×2)을 돌려준다."""
    상태들 = [np.asarray(x0, dtype=float)]
    for u in 입력들:
        상태들.append(A @ 상태들[-1] + B[:, 0] * u)
    return np.array(상태들)


def 비용(상태들: np.ndarray, 입력들: np.ndarray, Q: np.ndarray, R: float) -> tuple[float, float]:
    """목표(원점)에서 벗어난 정도의 합과 입력 크기의 합을 따로 돌려준다."""
    오차_비용 = float(sum(x @ Q @ x for x in 상태들[1:]))
    입력_비용 = float(R * np.sum(np.square(입력들)))
    return 오차_비용, 입력_비용
