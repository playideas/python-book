from collections.abc import Callable

import numpy as np

from 팔제어 import 성적, 제어기_만들기
from 현실팔 import 시뮬_물성, 실행, 현실_물성


def 저역통과(제어기: Callable, 알파: float) -> Callable:
    """행동 필터: 내보낼 토크를 1차 저역통과로 거른다. 알파 1이면 거르지 않는다."""
    거른 = None

    def 걸러_내기(t: float, 잰_각도: np.ndarray) -> np.ndarray:
        nonlocal 거른
        새_토크 = 제어기(t, 잰_각도)
        거른 = 새_토크 if 거른 is None else 거른 + 알파 * (새_토크 - 거른)
        return 거른
    return 걸러_내기


print("이득     알파 | 시뮬: 오차, 토크 떨림 | 현실: 오차, 못 감, 토크 떨림")
for kp, kd in [(40, 4), (110, 8)]:
    for 알파 in [1.0, 0.5, 0.3]:
        글 = []
        for 팔 in [시뮬_물성, 현실_물성]:
            기록들 = [실행(저역통과(제어기_만들기(kp, kd, 시뮬_물성), 알파), 8.0, 팔, 시드) for 시드 in range(5)]
            성적들 = [성적(기록) for 기록 in 기록들]
            # 토크 떨림: 한 주기 사이에 토크가 바뀐 크기의 평균(N·m)
            떨림 = np.mean([np.abs(np.diff(기록["토크"], axis=0)).mean() for 기록 in 기록들])
            글.append((np.mean([s[0] for s in 성적들]), sum(s[1] for s in 성적들), 떨림))
        (시_오차, _, 시_떨림), (현_오차, 현_못감, 현_떨림) = 글
        print(f"({kp:3d}, {kd}) {알파:.1f} | {시_오차:5.2f}도, {시_떨림:5.3f} | "
              f"{현_오차:5.2f}도, {현_못감:2d}/20, {현_떨림:5.3f}")
