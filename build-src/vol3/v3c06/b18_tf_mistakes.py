import json
import subprocess
import tempfile

import numpy as np
from rclpy.duration import Duration
from rclpy.time import Time
from tf2_ros import TransformException

from tf도구 import 상태_발행기, 연결, 여기

# 실수 1: 뿌리 링크에 inertial을 적었다 → robot_state_publisher가 경고를 남긴다
urdf6 = subprocess.run(["xacro", str(여기 / "예제팔.urdf.xacro")], capture_output=True, text=True, check=True).stdout
with tempfile.NamedTemporaryFile("w", suffix=".yaml") as 파일:
    json.dump({"robot_state_publisher": {"ros__parameters": {"robot_description": urdf6}}}, 파일)
    파일.flush()
    결과 = subprocess.run(["timeout", "2", "ros2", "run", "robot_state_publisher", "robot_state_publisher",
                         "--ros-args", "--params-file", 파일.name], capture_output=True, text=True)
경고 = next(줄 for 줄 in 결과.stderr.splitlines() if "kdl_parser" in 줄)
print("실수 1:", 경고.split("]: ", 1)[1].split(".")[0])

# 실수 2: joint_states에 관절 하나를 빠뜨렸다 → 그 아래 좌표계는 tf에 나타나지 않는다
with 상태_발행기((여기 / "두관절팔.urdf").read_text()), 연결() as 팔:
    시각 = 팔.관절_보내기(["shoulder"], [0.5], 확인=("base_link", "upper_arm"))    # elbow를 빠뜨림
    print("실수 2: upper_arm까지는 됨 →", bool(팔.버퍼.can_transform("base_link", "upper_arm", 시각)))
    try:
        팔.버퍼.lookup_transform("base_link", "tip", Time(), timeout=Duration(seconds=1))
    except TransformException as 오류:          # tf2 조회 오류들의 공통 부모
        print("        tip은 →", type(오류).__name__)
        print("       ", str(오류).split(" because ")[1].split(".")[0])
