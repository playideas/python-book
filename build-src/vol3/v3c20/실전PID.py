"""12장: 와인드업 방지, 측정값 미분, 미분 필터, 출력 한계, 앞먹임을 갖춘 PID."""
import numpy as np


class 실전PID:
    def __init__(self, kp: float, ki: float, kd: float, 주기: float, 출력_한계: float = np.inf,
                 와인드업: str = "클램핑", 미분_대상: str = "측정", 필터_알파: float = 1.0,
                 적분_구간: float = np.inf):
        self.kp, self.ki, self.kd, self.주기 = kp, ki, kd, 주기
        self.출력_한계, self.와인드업, self.미분_대상 = 출력_한계, 와인드업, 미분_대상
        self.필터_알파 = 필터_알파          # 1이면 거르지 않는다. 작을수록 많이 거른다
        self.적분_구간 = 적분_구간          # 오차가 이 안에 들어왔을 때만 적분한다(rad)
        # 역계산 이득: 적분 시간과 미분 시간의 기하 평균을 쓰는 흔한 관례
        적분_시간 = kp / ki if ki > 0 else np.inf
        미분_시간 = kd / kp if kd > 0 else 적분_시간
        self.역계산_이득 = 1 / np.sqrt(적분_시간 * 미분_시간)
        self.적분항 = 0.0                  # ki × (오차의 적분)을 바로 담는다
        self.거른_값 = None                # 미분할 신호를 1차 저역통과로 거른 값

    def __call__(self, 목표: float, 측정: float, 앞먹임: float = 0.0) -> float:
        오차 = 목표 - 측정
        대상 = -측정 if self.미분_대상 == "측정" else 오차      # 목표가 그대로면 둘의 변화는 같다
        if self.거른_값 is None:
            self.거른_값, 미분 = 대상, 0.0
        else:
            새_값 = self.거른_값 + self.필터_알파 * (대상 - self.거른_값)
            미분 = (새_값 - self.거른_값) / self.주기
            self.거른_값 = 새_값
        요청 = self.kp * 오차 + self.적분항 + self.kd * 미분 + 앞먹임
        출력 = float(np.clip(요청, -self.출력_한계, self.출력_한계))
        쌓을_오차 = 오차 if abs(오차) <= self.적분_구간 else 0.0
        if self.와인드업 == "없음":
            self.적분항 += self.ki * 쌓을_오차 * self.주기
        elif self.와인드업 == "클램핑":             # 포화를 더 깊게 만드는 쪽으로는 쌓지 않는다
            if 출력 == 요청 or np.sign(쌓을_오차) != np.sign(요청):
                self.적분항 += self.ki * 쌓을_오차 * self.주기
        else:                                        # 역계산: 잘려 나간 만큼 적분을 되돌린다
            self.적분항 += (self.ki * 쌓을_오차 + self.역계산_이득 * (출력 - 요청)) * self.주기
        return 출력
