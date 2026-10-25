import subprocess

import numpy as np

from tf도구 import 상태_발행기, 연결, 여기

urdf = subprocess.run(["xacro", str(여기 / "예제팔.urdf.xacro")], capture_output=True, text=True, check=True).stdout
관절_이름 = [f"joint{i}" for i in range(1, 7)]
좌표계_이름 = ["base_link"] + [f"link{i}" for i in range(1, 7)] + ["tip"]

with 상태_발행기(urdf), 연결() as 팔:
    시각 = 팔.관절_보내기(관절_이름, np.deg2rad([30, 45, 60, 0, 45, 0]))
    행렬들 = np.array([팔.변환("base_link", 이름, 시각) for 이름 in 좌표계_이름])   # T_바닥_좌표계
np.save("arm6_tf.npy", 행렬들)                      # (8, 4, 4): 좌표계 8개의 4×4 변환
print("좌표계:", 좌표계_이름)
print("저장: arm6_tf.npy", 행렬들.shape)
