"""12장: 가장 기본적인 이산 시간 PID. 제어 주기마다 한 번씩 부른다."""


class PID:
    def __init__(self, kp: float, ki: float, kd: float, 주기: float):
        self.kp, self.ki, self.kd, self.주기 = kp, ki, kd, 주기
        self.적분 = 0.0                 # 지금까지 쌓인 오차 × 시간
        self.이전_오차 = None           # 미분을 위해 한 주기 전 오차를 기억한다

    def __call__(self, 목표: float, 측정: float) -> float:
        오차 = 목표 - 측정
        self.적분 += 오차 * self.주기
        미분 = 0.0 if self.이전_오차 is None else (오차 - self.이전_오차) / self.주기
        self.이전_오차 = 오차
        return self.kp * 오차 + self.ki * self.적분 + self.kd * 미분
