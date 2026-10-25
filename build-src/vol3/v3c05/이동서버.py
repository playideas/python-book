"""5.9절: 1장의 점 로봇을 목표까지 움직이는 액션 서버. 시간은 10배 빠르게 흘린다."""
import time

import numpy as np
import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node
from robot_interfaces.action import MoveTo

from 점로봇 import 움직이기

주기, 이득 = 0.1, 1.5
최대_거리 = 5.0          # m. 이보다 먼 목표는 받지 않는다


class 이동서버(Node):
    def __init__(self):
        super().__init__("move_server")
        self.위치 = np.array([0.0, 0.0])
        ActionServer(self, MoveTo, "move_to", execute_callback=self.실행,
                     goal_callback=self.목표_검사, cancel_callback=lambda 요청: CancelResponse.ACCEPT)

    def 목표_검사(self, 목표: MoveTo.Goal) -> GoalResponse:
        거리 = np.linalg.norm(np.array([목표.x, 목표.y]) - self.위치)
        return GoalResponse.ACCEPT if 거리 <= 최대_거리 else GoalResponse.REJECT

    def 실행(self, 목표_핸들) -> MoveTo.Result:
        목표 = np.array([목표_핸들.request.x, 목표_핸들.request.y])
        for 걸음 in range(1, 101):                       # 최대 10초(100걸음)
            if 목표_핸들.is_cancel_requested:             # 취소 요청이 왔으면 그 자리에 선다
                목표_핸들.canceled()
                return MoveTo.Result(error=float(np.linalg.norm(목표 - self.위치)))
            self.위치 = 움직이기(self.위치, 이득 * (목표 - self.위치), 주기)
            남은 = float(np.linalg.norm(목표 - self.위치))
            if 걸음 % 10 == 0:                             # 1초마다 중간 소식을 보낸다
                목표_핸들.publish_feedback(MoveTo.Feedback(remaining=남은))
            if 남은 < 0.01:
                break
            time.sleep(주기 / 10)                         # 진짜 시간보다 10배 빠르게
        목표_핸들.succeed()
        return MoveTo.Result(error=남은)


def main() -> None:
    try:
        with rclpy.init():
            rclpy.spin(이동서버(), executor=MultiThreadedExecutor())   # 실행 중에도 취소를 받으려면 여러 스레드로
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == "__main__":
    main()
