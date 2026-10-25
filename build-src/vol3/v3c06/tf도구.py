"""6장 도구: robot_state_publisher를 띄우고, 관절 각도를 보내고, tf2로 변환을 묻는다."""
import json
import subprocess
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from scipy.spatial.transform import Rotation
from sensor_msgs.msg import JointState
from tf2_ros import Buffer, TransformListener

여기 = Path(__file__).parent              # 이 파일과 URDF가 있는 폴더


@contextmanager
def 상태_발행기(urdf_글: str):
    """robot_state_publisher 노드를 따로 띄웠다가, with 블록이 끝나면 내린다.
    URDF 글은 파라미터 파일로 넘긴다. 명령줄 -p로 넘기면 xacro가 붙인 머리 주석 때문에 해석에 실패한다."""
    with tempfile.NamedTemporaryFile("w", suffix=".yaml") as 파일:
        설정 = {"robot_state_publisher": {"ros__parameters": {"robot_description": urdf_글}}}
        json.dump(설정, 파일)                          # JSON은 YAML로도 읽힌다
        파일.flush()
        명령 = ["ros2", "run", "robot_state_publisher", "robot_state_publisher",
              "--ros-args", "--params-file", 파일.name]
        프로세스 = subprocess.Popen(명령, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            yield 프로세스
        finally:
            프로세스.terminate()
            프로세스.wait()


def 행렬로(변환_메시지) -> np.ndarray:
    """TransformStamped → 4×4 동차 변환 행렬. ROS 쿼터니언은 x, y, z, w 이름 칸이다."""
    t, q = 변환_메시지.transform.translation, 변환_메시지.transform.rotation
    T = np.eye(4)
    T[:3, :3] = Rotation.from_quat([q.x, q.y, q.z, q.w]).as_matrix()
    T[:3, 3] = [t.x, t.y, t.z]
    return T


class 팔연결(Node):
    """/joint_states로 관절 각도를 보내고, tf2 버퍼에서 변환을 꺼내는 노드."""

    def __init__(self) -> None:
        super().__init__("arm_client")
        self.발행기 = self.create_publisher(JointState, "joint_states", 10)
        self.버퍼 = Buffer()
        self.듣개 = TransformListener(self.버퍼, self, spin_thread=True)   # 받는 일은 따로 도는 스레드가
        마감 = time.monotonic() + 10
        while self.발행기.get_subscription_count() == 0:                  # 받는 쪽이 붙을 때까지
            if time.monotonic() > 마감:
                raise TimeoutError("joint_states를 받는 노드(robot_state_publisher)가 없다")
            time.sleep(0.05)

    def 관절_보내기(self, 이름들: list[str], 각들, 확인=("base_link", "tip")) -> Time:
        """관절 각도(rad)를 발행하고 메시지에 찍은 시각을 돌려준다.
        처음 몇 번은 받는 쪽이 아직 연결 중이라 놓칠 수 있어서, tf2에 그 시각의 변환이 생길 때까지 다시 보낸다."""
        while True:
            지금 = self.get_clock().now()
            메시지 = JointState(name=list(이름들), position=[float(각) for 각 in 각들])
            메시지.header.stamp = 지금.to_msg()
            self.발행기.publish(메시지)
            if self.버퍼.can_transform(*확인, 지금, timeout=Duration(seconds=0.2)):
                return 지금

    def 변환(self, 기준: str, 대상: str, 시각: Time | None = None) -> np.ndarray:
        """tf2에 묻는다: 대상 좌표계를 기준 좌표계에서 본 4×4 변환(T_기준_대상)."""
        메시지 = self.버퍼.lookup_transform(기준, 대상, 시각 or Time(), timeout=Duration(seconds=5))
        return 행렬로(메시지)


@contextmanager
def 연결():
    """rclpy를 켜고 팔연결 노드 하나를 만든다."""
    rclpy.init()
    노드 = 팔연결()
    try:
        yield 노드
    finally:
        노드.destroy_node()
        rclpy.shutdown()
