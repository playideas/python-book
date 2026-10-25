"""5.2절: 0.5초마다 박자를 세는 첫 번째 노드."""
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class 첫노드(Node):
    def __init__(self):
        super().__init__("first_node")                      # ROS 안에서 부르는 이름
        self.박자 = 0
        self.타이머 = self.create_timer(0.5, self.박자_세기)  # 0.5초마다 박자_세기를 부른다
        self.get_logger().info("노드를 시작했다")

    def 박자_세기(self) -> None:
        self.박자 += 1
        self.get_logger().info(f"{self.박자}번째 박자")
        if self.박자 == 3:                                   # 책에서는 세 박자만 세고 끝낸다
            self.get_logger().info("세 박자를 셌으니 끝낸다")
            rclpy.shutdown()


def main() -> None:
    try:
        with rclpy.init():            # ROS 2 통신을 준비하고, 블록을 나갈 때 정리한다
            노드 = 첫노드()
            rclpy.spin(노드)          # 타이머·메시지가 올 때마다 콜백을 불러 주며 기다린다
    except (KeyboardInterrupt, ExternalShutdownException):
        pass                          # Ctrl+C나 바깥의 종료 요청은 정상 종료로 본다


if __name__ == "__main__":
    main()
