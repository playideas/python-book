"""5.11절 실습, 판단: 잰 위치를 받아 비례 제어로 속도 명령을 내는 노드."""
import numpy as np
import rclpy
from geometry_msgs.msg import PointStamped, TwistStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class 판단(Node):
    def __init__(self):
        super().__init__("judge")
        self.declare_parameter("gain", 1.5)                 # 남은 거리 1m당 몇 m/s로 갈까
        self.declare_parameter("goal", [2.0, 1.0])          # 목표 위치(m)
        self.발행자 = self.create_publisher(TwistStamped, "cmd_vel", 10)
        self.create_subscription(PointStamped, "measured_position", self.판단하기, 10)

    def 판단하기(self, 잰: PointStamped) -> None:
        이득 = self.get_parameter("gain").value            # 매번 읽으니 도는 중에 바꿔도 바로 반영된다
        목표 = np.array(self.get_parameter("goal").value)
        속도 = 이득 * (목표 - np.array([잰.point.x, 잰.point.y]))
        명령 = TwistStamped()
        명령.header.stamp = 잰.header.stamp                 # 어느 측정을 보고 낸 명령인지 표시한다
        명령.twist.linear.x, 명령.twist.linear.y = float(속도[0]), float(속도[1])
        self.발행자.publish(명령)


def main() -> None:
    try:
        with rclpy.init():
            rclpy.spin(판단())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
