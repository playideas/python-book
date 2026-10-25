"""5.11절 실습, 감지: 진짜 위치를 받아 잡음 섞인 측정값으로 내보내는 위치 센서 노드."""
import numpy as np
import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.time import Time

from point_robot.점로봇 import 위치_재기


class 위치센서(Node):
    def __init__(self):
        super().__init__("position_sensor")
        self.잡음 = self.declare_parameter("noise", 0.0).value       # m
        self.씨앗 = self.declare_parameter("seed", 1).value
        self.발행자 = self.create_publisher(PointStamped, "measured_position", 10)
        self.create_subscription(PointStamped, "true_position", self.재기, 10)

    def 재기(self, 진짜: PointStamped) -> None:
        # 같은 시각의 측정은 몇 번을 다시 재도 같은 잡음이 나오게 시각으로 난수를 정한다
        생성기 = np.random.default_rng([self.씨앗, Time.from_msg(진짜.header.stamp).nanoseconds])
        잰_위치 = 위치_재기(np.array([진짜.point.x, 진짜.point.y]), 생성기, self.잡음)
        잰 = PointStamped()
        잰.header = 진짜.header                                     # 언제, 어느 좌표계로 잰 값인지 그대로
        잰.point.x, 잰.point.y = float(잰_위치[0]), float(잰_위치[1])
        self.발행자.publish(잰)


def main() -> None:
    try:
        with rclpy.init():
            rclpy.spin(위치센서())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
