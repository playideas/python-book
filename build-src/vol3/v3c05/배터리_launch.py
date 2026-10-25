"""5.10절: 로봇 두 대의 배터리 노드를 한 번에 띄우는 launch 파일."""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    노드들 = []
    for 로봇 in ["robot1", "robot2"]:                 # 같은 노드를 이름공간만 바꿔 두 벌 띄운다
        노드들.append(Node(package="battery_demo", executable="battery_monitor", namespace=로봇, output="screen"))
        노드들.append(Node(package="battery_demo", executable="battery_publisher", namespace=로봇, output="screen"))
    return LaunchDescription(노드들)
