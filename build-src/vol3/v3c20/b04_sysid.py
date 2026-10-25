import numpy as np

from 식별 import 식별, 이름들
from 현실팔 import 실행, 현실_물성


def 들뜸(t: float, q: np.ndarray) -> np.ndarray:
    return np.array([3.0 * np.sin(2 * np.pi * 0.7 * t) + 2.0 * np.sin(2 * np.pi * 1.9 * t),
                     1.2 * np.sin(2 * np.pi * 1.1 * t) + 0.8 * np.sin(2 * np.pi * 2.7 * t)])


기록 = 실행(들뜸, 6.0, 현실_물성, 시드=1)        # 현실 역할 팔에서 6초 동안 기록한 것(잰 각도만 쓴다)
찾은, rms = 식별(들뜸, 기록)
print(f"고른 지연: {찾은.지연}틱({찾은.지연 * 10}ms), 남은 차이 {rms:.2f}도")
print("정답지와 비교: " + ", ".join(f"{이름} {getattr(찾은, 이름):.3f}(참 {getattr(현실_물성, 이름)})"
                              for 이름 in 이름들))
