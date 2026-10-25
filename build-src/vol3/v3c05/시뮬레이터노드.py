"""5.11절 실습, 행동: 속도 명령을 받아 점 로봇을 한 걸음씩 움직이는 시뮬레이터 노드."""
import numpy as np
import rclpy
from geometry_msgs.msg import PointStamped, TwistStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.time import Time

from point_robot.점로봇 import 움직이기


class 시뮬레이터(Node):
    def __init__(self):
        super().__init__("simulator")
        self.주기 = self.declare_parameter("period", 0.1).value       # 한 걸음의 시뮬레이션 시간(초)
        self.걸음_수 = self.declare_parameter("steps", 80).value
        self.미끄러짐 = self.declare_parameter("slip", 0.0).value
        self.기록_파일 = self.declare_parameter("record", "").value  # 경로를 남길 CSV 파일 이름
        self.걸음, self.위치 = 0, np.array([0.0, 0.0])
        self.경로 = [self.위치]
        self.발행자 = self.create_publisher(PointStamped, "true_position", 10)
        self.create_subscription(TwistStamped, "cmd_vel", self.명령_받기, 10)
        self.지난_걸음 = -1
        self.create_timer(0.5, self.멈췄으면_다시_알리기)

    def 지금_시각(self) -> int:
        return round(self.걸음 * self.주기 * 1e9)                   # 시뮬레이션 시각(나노초)

    def 위치_알리기(self) -> None:
        메시지 = PointStamped()
        메시지.header.stamp = Time(nanoseconds=self.지금_시각()).to_msg()
        메시지.header.frame_id = "world"
        메시지.point.x, 메시지.point.y = float(self.위치[0]), float(self.위치[1])
        self.발행자.publish(메시지)

    def 멈췄으면_다시_알리기(self) -> None:
        # 처음 연결될 때처럼 메시지가 사라져 0.5초 동안 한 걸음도 못 갔으면 지금 위치를 다시 알린다
        if self.걸음 == self.지난_걸음:
            self.위치_알리기()
        self.지난_걸음 = self.걸음

    def 명령_받기(self, 명령: TwistStamped) -> None:
        if Time.from_msg(명령.header.stamp).nanoseconds != self.지금_시각():
            return                                                  # 지난 걸음에 대한 명령은 버린다
        생성기 = np.random.default_rng([7, self.걸음])                # 걸음마다 정해진 미끄러짐
        속도 = np.array([명령.twist.linear.x, 명령.twist.linear.y])
        self.위치 = 움직이기(self.위치, 속도, self.주기, 생성기, self.미끄러짐)
        self.걸음 += 1
        self.경로.append(self.위치)
        if self.걸음 % 10 == 0:
            self.get_logger().info(f"{self.걸음 * self.주기:.1f}초: 위치 {np.round(self.위치, 3)}")
        if self.걸음 < self.걸음_수:
            self.위치_알리기()
        else:
            self.끝내기()

    def 끝내기(self) -> None:
        if self.기록_파일:
            np.savetxt(self.기록_파일, np.array(self.경로), delimiter=",", header="x,y", comments="")
        self.get_logger().info(f"{self.걸음}걸음 끝. 마지막 위치 {np.round(self.위치, 3)}")
        rclpy.shutdown()


def main() -> None:
    try:
        with rclpy.init():
            rclpy.spin(시뮬레이터())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
