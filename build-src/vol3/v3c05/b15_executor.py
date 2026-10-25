import time

import rclpy
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor, SingleThreadedExecutor
from rclpy.node import Node


class 한몸로봇(Node):
    """모터 고리(0.01초마다)와 느린 카메라 처리(0.5초마다, 한 번에 0.2초)를 한 노드에 넣었다."""

    def __init__(self, 무리_나누기: bool):
        super().__init__("one_body_robot")
        모터_무리 = MutuallyExclusiveCallbackGroup() if 무리_나누기 else None
        카메라_무리 = MutuallyExclusiveCallbackGroup() if 무리_나누기 else None
        self.모터_시각들 = []
        self.create_timer(0.01, self.모터, callback_group=모터_무리)
        self.create_timer(0.5, self.카메라, callback_group=카메라_무리)

    def 모터(self) -> None:
        self.모터_시각들.append(time.monotonic())

    def 카메라(self) -> None:
        time.sleep(0.2)                     # 사진에서 물체를 찾느라 0.2초 걸린다


def 재기(실행기, 무리_나누기: bool) -> None:
    노드 = 한몸로봇(무리_나누기)
    실행기.add_node(노드)
    끝 = time.monotonic() + 2.0
    while time.monotonic() < 끝:            # 2초 동안 돌린다
        실행기.spin_once(timeout_sec=0.01)
    실행기.remove_node(노드)
    간격들 = [b - a for a, b in zip(노드.모터_시각들, 노드.모터_시각들[1:])]
    print(f"{type(실행기).__name__:22s}: 모터 고리의 가장 긴 간격 {max(간격들):.1f}초")
    노드.destroy_node()


with rclpy.init():
    재기(SingleThreadedExecutor(), 무리_나누기=False)
    재기(MultiThreadedExecutor(num_threads=2), 무리_나누기=True)
