"""18장: DAgger. 정책이 직접 움직이고, 들른 상태마다 전문가에게 답을 물어 데이터에 보탠다."""
import numpy as np

from 모방환경 import 상자_범위
from 시연도구 import 굴리기
from 정책도구 import 학습


def 다거(관측, 행동, 회차: int = 5, 에피소드: int = 25, 흔들림: float = 0.004, 씨앗: int = 7):
    """처음 시연으로 BC를 학습한 뒤, 굴리기 → 묻기 → 모으기 → 다시 학습을 회차만큼."""
    생성기 = np.random.default_rng(씨앗)
    관측들, 행동들 = [관측], [행동]
    정책 = 학습(관측, 행동)
    for 회 in range(1, 회차 + 1):
        성공 = 0
        for i in range(에피소드):
            o, a, s = 굴리기(생성기.uniform(*상자_범위), 정책, 물어보기=True, 흔들림=흔들림, 씨앗=회 * 1000 + i)
            관측들.append(o)                 # 정책이 들른 상태와
            행동들.append(a)                 # 그 상태에서 전문가가 했을 행동
            성공 += s
        정책 = 학습(np.concatenate(관측들), np.concatenate(행동들))
        print(f"{회}회차: 지난 정책으로 {에피소드}번 중 {성공}번 성공, 모은 걸음 {sum(map(len, 관측들)):,}개")
    return 정책
