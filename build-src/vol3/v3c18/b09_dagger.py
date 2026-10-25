import os
from pathlib import Path

import torch

from 다거 import 다거
from 시연도구 import 성공률, 시연_모으기, 시험_위치

데이터 = 시연_모으기(250)
처음_칸 = 데이터["에피소드"] < 25                      # 깨끗한 시연 25개에서 출발
정책 = 다거(데이터["관측"][처음_칸], 데이터["행동"][처음_칸], 회차=5, 에피소드=25, 흔들림=0.004)
시험 = 시험_위치(50)
print(f"DAgger 정책: 흔들림 0.004에서 {성공률(정책, 시험, 0.004):.0%}, 흔들림 없이 {성공률(정책, 시험):.0%}")

저장 = Path(os.environ.get("BOOK_DATA_DIR", "data")) / "ch18" / "dagger.pt"
torch.save(정책, 저장, pickle_protocol=4)   # 18.9절 실습에서 다시 쓴다. 한글 모듈 이름은 4판 이상이 필요
