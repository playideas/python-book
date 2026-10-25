import rclpy
from rclpy.exceptions import InvalidNodeNameException, InvalidTopicNameException
from rclpy.node import Node
from std_msgs.msg import Float32

with rclpy.init():
    for 이름 in ["battery_monitor", "배터리감시", "battery-monitor"]:
        try:
            Node(이름).destroy_node()
            print(f"노드 이름 {이름!r}: 됨")
        except InvalidNodeNameException:
            print(f"노드 이름 {이름!r}: 안 됨")
    노드 = Node("name_test")
    for 토픽 in ["battery_voltage", "robot1/battery_voltage", "배터리", "2nd_battery"]:
        try:
            발행자 = 노드.create_publisher(Float32, 토픽, 10)
            print(f"토픽 이름 {토픽!r}: 됨 → 전체 이름 {발행자.topic_name}")
        except InvalidTopicNameException:
            print(f"토픽 이름 {토픽!r}: 안 됨")
