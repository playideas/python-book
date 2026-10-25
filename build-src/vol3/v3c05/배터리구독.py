"""5.3절: 배터리 전압을 구독해 낮으면 경고하는 노드."""
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Float32

경고_전압 = 12.0          # V. 이보다 낮으면 충전하러 가야 한다


class 배터리감시(Node):
    def __init__(self):
        super().__init__("battery_monitor")
        self.create_subscription(Float32, "battery_voltage", self.받기, 10)

    def 받기(self, 메시지: Float32) -> None:          # 메시지가 올 때마다 불린다
        if 메시지.data < 경고_전압:
            self.get_logger().warning(f"받음: {메시지.data:.1f}V, 충전이 필요하다")
        else:
            self.get_logger().info(f"받음: {메시지.data:.1f}V")


def main() -> None:
    try:
        with rclpy.init():
            rclpy.spin(배터리감시())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == "__main__":
    main()
