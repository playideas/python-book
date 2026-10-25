import rclpy
from rclpy.event_handler import SubscriptionEventCallbacks
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, qos_profile_sensor_data
from std_msgs.msg import Int32

믿음 = ReliabilityPolicy.RELIABLE         # 등기 우편: 받았는지 확인하고, 못 받았으면 다시 보낸다
최선 = ReliabilityPolicy.BEST_EFFORT      # 전단지: 보내기만 하고 확인하지 않는다


def 실험(노드: Node, 발행_쪽: ReliabilityPolicy, 구독_쪽: ReliabilityPolicy, 토픽: str) -> None:
    받은 = []
    사건 = SubscriptionEventCallbacks(        # QoS가 맞지 않을 때 불리는 콜백
        incompatible_qos=lambda 정보: 받은.append(
            "맞지 않는 정책: " + 정보.last_policy_kind.name.removeprefix("RMW_QOS_POLICY_")))
    발행자 = 노드.create_publisher(Int32, 토픽, QoSProfile(depth=10, reliability=발행_쪽))
    노드.create_subscription(Int32, 토픽, lambda m: 받은.append(m.data),
                         QoSProfile(depth=10, reliability=구독_쪽), event_callbacks=사건)
    for _ in range(20):                       # 서로 찾을 시간(약 1초)
        rclpy.spin_once(노드, timeout_sec=0.05)
    for i in range(5):
        발행자.publish(Int32(data=i))
    for _ in range(20):                       # 메시지가 도착할 시간
        rclpy.spin_once(노드, timeout_sec=0.05)
    print(f"발행 {발행_쪽.name:11s} → 구독 {구독_쪽.name:11s}: 연결 {발행자.get_subscription_count()}개, 받은 것 {받은}")


with rclpy.init():
    노드 = Node("qos_test")
    for 번호, (발행_쪽, 구독_쪽) in enumerate([(믿음, 믿음), (최선, 최선), (믿음, 최선), (최선, 믿음)]):
        실험(노드, 발행_쪽, 구독_쪽, f"qos_demo_{번호}")

# 자주 쓰는 두 가지: 숫자 10만 적었을 때와 센서용으로 미리 정해 둔 프로파일
for 이름, 프로파일 in [("숫자 10", QoSProfile(depth=10)), ("qos_profile_sensor_data", qos_profile_sensor_data)]:
    print(f"{이름}: {프로파일.reliability.name}, {프로파일.history.name} {프로파일.depth}, {프로파일.durability.name}")
