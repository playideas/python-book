"""5.5절: 모터를 켜고 끄는 서비스를 제공하는 노드."""
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_srvs.srv import SetBool


class 모터드라이버(Node):
    def __init__(self):
        super().__init__("motor_driver")
        self.켜짐 = False
        self.create_service(SetBool, "enable_motor", self.요청_처리)   # 타입, 서비스 이름, 콜백

    def 요청_처리(self, 요청: SetBool.Request, 응답: SetBool.Response) -> SetBool.Response:
        if 요청.data == self.켜짐:                     # 이미 그 상태면 거절한다
            응답.success = False
            응답.message = "이미 켜져 있다" if self.켜짐 else "이미 꺼져 있다"
        else:
            self.켜짐 = 요청.data
            응답.success = True
            응답.message = "모터를 켰다" if self.켜짐 else "모터를 껐다"
        self.get_logger().info(f"요청 {요청.data} → {응답.message}")
        return 응답


def main() -> None:
    try:
        with rclpy.init():
            rclpy.spin(모터드라이버())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == "__main__":
    main()
