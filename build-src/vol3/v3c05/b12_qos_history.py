import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from std_msgs.msg import String


def 기다리기(노드: Node, 횟수: int = 20) -> None:
    for _ in range(횟수):                          # 0.05초씩 돌며 콜백을 처리한다
        rclpy.spin_once(노드, timeout_sec=0.05)


with rclpy.init():
    노드 = Node("qos_history")

    # 1) 기록 깊이: 구독자가 바빠서 못 꺼내 가는 동안 메시지 10개가 쌓이면?
    for 깊이 in [3, 10]:
        받은 = []
        발행자 = 노드.create_publisher(String, f"burst_{깊이}", QoSProfile(depth=깊이))
        노드.create_subscription(String, f"burst_{깊이}", lambda m, 받은=받은: 받은.append(m.data),
                             QoSProfile(depth=깊이))
        기다리기(노드)
        for i in range(10):                        # 콜백을 처리하지 않는 동안 10개를 몰아서 보낸다
            발행자.publish(String(data=str(i)))
        기다리기(노드)
        print(f"깊이 {깊이:2d}: 받은 것 {받은}")

    # 2) 지속성: 구독자가 늦게 들어오면 지난 메시지를 받을 수 있나?
    게시판 = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
    발행자 = 노드.create_publisher(String, "map", 게시판)
    for 판 in ["지도 1판", "지도 2판"]:            # 구독자가 아무도 없을 때 보낸다
        발행자.publish(String(data=판))
    for 이름, 지속성 in [("VOLATILE", DurabilityPolicy.VOLATILE),
                       ("TRANSIENT_LOCAL", DurabilityPolicy.TRANSIENT_LOCAL)]:
        받은 = []
        노드.create_subscription(String, "map", lambda m, 받은=받은: 받은.append(m.data),
                             QoSProfile(depth=1, durability=지속성))
        기다리기(노드)
        print(f"늦게 온 구독자({이름:15s}): 받은 것 {받은}")
