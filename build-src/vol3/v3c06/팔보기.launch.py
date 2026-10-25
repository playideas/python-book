"""예제 팔을 화면에 띄우는 launch 파일: xacro → robot_state_publisher, 관절 슬라이더 대신 joint_state_publisher, RViz."""
from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

xacro_파일 = Path(__file__).with_name("예제팔.urdf.xacro")


def generate_launch_description() -> LaunchDescription:
    # xacro를 실행한 결과 글을 그대로 파라미터 값으로(문자열이라고 못 박아 둔다)
    설명 = ParameterValue(Command(["xacro ", str(xacro_파일)]), value_type=str)
    return LaunchDescription([
        DeclareLaunchArgument("rviz", default_value="true"),
        Node(package="robot_state_publisher", executable="robot_state_publisher",
             parameters=[{"robot_description": 설명}]),
        Node(package="joint_state_publisher", executable="joint_state_publisher",
             parameters=[{"zeros.joint2": 0.7854, "zeros.joint3": 1.0472}]),
        Node(package="rviz2", executable="rviz2", condition=IfCondition(LaunchConfiguration("rviz"))),
    ])
