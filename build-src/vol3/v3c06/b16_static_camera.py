import subprocess

import numpy as np

from tf도구 import 상태_발행기, 연결, 여기
from 팔도구 import 변환, 순기구학
from 회전도구 import Rz, 깔끔

urdf = subprocess.run(["xacro", str(여기 / "예제팔.urdf.xacro")], capture_output=True, text=True, check=True).stdout
관절_이름 = [f"joint{i}" for i in range(1, 7)]
# 손목(link6) 옆 4cm에 카메라를 나사로 고정했다: 정적 변환. 렌즈(z)는 도구 방향, 90도 돌려 달았다
카메라_설치 = subprocess.Popen(
    ["ros2", "run", "tf2_ros", "static_transform_publisher", "--x", "0.04", "--z", "0.02",
     "--yaw", str(np.pi / 2), "--frame-id", "link6", "--child-frame-id", "camera"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
T_손목_카메라 = 변환(Rz(90), [0.04, 0.0, 0.02])             # 같은 설치를 행렬로
컵_카메라 = np.array([0.02, -0.01, 0.25, 1.0])              # 카메라가 본 컵(카메라 기준)

with 상태_발행기(urdf), 연결() as 팔:
    for 관절각_도 in [[30, 45, 60, 0, 45, 0], [-20, 30, 70, 0, 60, 0]]:
        관절각 = np.deg2rad(관절각_도)
        시각 = 팔.관절_보내기(관절_이름, 관절각)
        T_바닥_카메라 = 팔.변환("base_link", "camera", 시각)          # 동적 사슬 + 정적 변환
        직접 = 순기구학(관절각)[5] @ T_손목_카메라                  # T_바닥_손목 @ T_손목_카메라
        print(f"자세 {관절각_도}")
        print("  tf2로 구한 바닥 기준 컵:", 깔끔((T_바닥_카메라 @ 컵_카메라)[:3]))
        print("  행렬로 구한 바닥 기준 컵:", 깔끔((직접 @ 컵_카메라)[:3]))
카메라_설치.terminate()
카메라_설치.wait()
