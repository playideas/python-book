"""5.3절: 배터리 전압을 0.2초마다 발행하는 노드(전압은 예제용으로 만든 값)."""
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Float32


class 배터리발행(Node):
    def __init__(self):
        super().__init__("battery_publisher")
        self.발행자 = self.create_publisher(Float32, "battery_voltage", 10)   # 타입, 토픽 이름, 큐 깊이
        self.보낸_수 = 0
        self.create_timer(0.2, self.보내기)

    def 보내기(self) -> None:
        if self.발행자.get_subscription_count() == 0:      # 아무도 안 듣고 있으면 기다린다
            return
        메시지 = Float32()
        메시지.data = 12.5 - 0.2 * self.보낸_수              # 예제용: 한 번에 0.2V씩 떨어진다
        self.발행자.publish(메시지)
        self.get_logger().info(f"보냄: {메시지.data:.1f}V")
        self.보낸_수 += 1
        if self.보낸_수 == 5:                               # 책에서는 다섯 번만 보내고 끝낸다
            rclpy.shutdown()


def main() -> None:
    try:
        with rclpy.init():
            rclpy.spin(배터리발행())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == "__main__":
    main()
