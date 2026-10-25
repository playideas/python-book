import numpy as np

from 모방환경 import 제어_주기
from 시연도구 import 시연_모으기
from 회전도구 import 깔끔

데이터 = 시연_모으기(250)                    # 처음이면 250번 시연을 돌리고, 다음부터는 저장한 것을 읽는다
for 이름, 값 in 데이터.items():
    print(f"{이름:5s}: 모양 {값.shape}, 자료형 {값.dtype}")
길이 = np.bincount(데이터["에피소드"]) * 제어_주기
print(f"에피소드 {len(길이)}개, 길이 평균 {길이.mean():.2f}초 (가장 짧게 {길이.min():.2f}초, 길게 {길이.max():.2f}초)")
print("첫 걸음 관측:", 깔끔(데이터["관측"][0]))
print("첫 걸음 행동:", 깔끔(데이터["행동"][0], 4))
