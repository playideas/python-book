"""5.6절: 최대 속도를 파라미터로 받는 노드. 바꿀 때마다 값을 검사한다."""
import rclpy
from rcl_interfaces.msg import SetParametersResult
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.parameter import Parameter

안전_한계 = 1.0     # m/s. 누가 뭐라 해도 이보다 빠르게는 못 바꾼다


class 속도제한(Node):
    def __init__(self):
        super().__init__("speed_limiter")
        self.add_on_set_parameters_callback(self.바꾸기_전_검사)   # 검사부터 걸어 두고
        self.declare_parameter("max_speed", 0.5)        # 선언한다: 이름과 기본값(타입은 기본값으로 정해진다)
        self.declare_parameter("robot_name", "pointbot")
        최대 = self.get_parameter("max_speed").value
        이름 = self.get_parameter("robot_name").value
        self.get_logger().info(f"{이름}의 최대 속도 {최대}m/s로 시작")

    def 바꾸기_전_검사(self, 바뀔_것들: list[Parameter]) -> SetParametersResult:
        for p in 바뀔_것들:
            if p.name == "max_speed" and not 0.0 < p.value <= 안전_한계:
                return SetParametersResult(successful=False, reason=f"0보다 크고 {안전_한계} 이하여야 한다")
            self.get_logger().info(f"{p.name} = {p.value}")
        return SetParametersResult(successful=True)


def main() -> None:
    try:
        with rclpy.init():
            rclpy.spin(속도제한())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == "__main__":
    main()
