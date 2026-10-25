"""5.9절: 이동 액션 클라이언트. 끝까지 가기, 너무 먼 목표, 도중에 취소하기를 차례로 해 본다."""
import rclpy
from action_msgs.msg import GoalStatus
from rclpy.action import ActionClient
from rclpy.node import Node
from robot_interfaces.action import MoveTo


def 보내기(노드: Node, 클라이언트: ActionClient, x: float, y: float, 취소_시점: int = 0) -> None:
    """목표를 보내고 결과까지 기다린다. 취소_시점이 있으면 그만큼 피드백을 받은 뒤 취소한다."""
    피드백_수 = 0

    def 피드백_받기(메시지) -> None:
        nonlocal 피드백_수
        피드백_수 += 1
        print(f"  피드백: 남은 거리 {메시지.feedback.remaining:.3f}m")

    미래 = 클라이언트.send_goal_async(MoveTo.Goal(x=x, y=y), feedback_callback=피드백_받기)
    rclpy.spin_until_future_complete(노드, 미래)
    핸들 = 미래.result()                                   # 서버가 목표를 받아들였는가
    print(f"목표 ({x}, {y}) → {'받아들여짐' if 핸들.accepted else '거절됨'}")
    if not 핸들.accepted:
        return
    결과_미래 = 핸들.get_result_async()
    while not 결과_미래.done():
        rclpy.spin_once(노드, timeout_sec=0.1)
        if 피드백_수 == 취소_시점 > 0:
            print("  취소를 요청한다")
            rclpy.spin_until_future_complete(노드, 핸들.cancel_goal_async())
            취소_시점 = 0
    결과 = 결과_미래.result()
    if 결과.status == GoalStatus.STATUS_SUCCEEDED:
        print(f"  성공: 남은 거리 {결과.result.error:.3f}m")
    elif 결과.status == GoalStatus.STATUS_CANCELED:
        print("  취소됨: 그 자리에 섰다")


with rclpy.init():
    노드 = Node("move_client")
    클라이언트 = ActionClient(노드, MoveTo, "move_to")
    클라이언트.wait_for_server(timeout_sec=5.0)
    보내기(노드, 클라이언트, 2.0, 1.0)
    보내기(노드, 클라이언트, 9.0, 9.0)
    보내기(노드, 클라이언트, 0.0, 0.0, 취소_시점=2)
