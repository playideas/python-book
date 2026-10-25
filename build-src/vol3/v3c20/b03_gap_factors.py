from dataclasses import fields, replace

import numpy as np

from 팔제어 import 돌려_보기
from 현실팔 import 시뮬_물성, 실행, 현실_물성


def 들뜸(t: float, q: np.ndarray) -> np.ndarray:
    return np.array([3.0 * np.sin(2 * np.pi * 0.7 * t) + 2.0 * np.sin(2 * np.pi * 1.9 * t),
                     1.2 * np.sin(2 * np.pi * 1.1 * t) + 0.8 * np.sin(2 * np.pi * 2.7 * t)])


기준 = 실행(들뜸, 6.0, 시뮬_물성)["잰_각도"]
print("현실에서 가져온 차이 하나 | 열린 고리 차이 RMS | 시뮬 이득(110, 8)의 평균 오차, 못 감")
for 칸 in fields(시뮬_물성):
    하나만 = replace(시뮬_물성, **{칸.name: getattr(현실_물성, 칸.name)})      # 이 차이 하나만 현실 값으로
    열린 = np.rad2deg(np.sqrt(np.mean((실행(들뜸, 6.0, 하나만, 시드=1)["잰_각도"] - 기준) ** 2)))
    오차, 못감 = 돌려_보기(110, 8, 시뮬_물성, 하나만)
    단위 = np.rad2deg(1) if 칸.name in ("잡음", "유격") else 1          # 이 둘은 도로 보여 준다
    print(f"{칸.name:6s}: {getattr(시뮬_물성, 칸.name) * 단위:.3g} → {getattr(현실_물성, 칸.name) * 단위:.3g} | "
          f"{열린:6.2f}도 | {오차:5.2f}도, {못감}/4")
