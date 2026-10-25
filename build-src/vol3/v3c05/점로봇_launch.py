"""5.11절 실습: 센서·판단·시뮬레이터 세 노드를 한 번에 띄운다."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def 실수_인자(이름: str) -> ParameterValue:
    """명령줄에서 받은 글자를 실수 파라미터로 넘긴다(gain:=2처럼 정수로 적어도 2.0이 된다)."""
    return ParameterValue(LaunchConfiguration(이름), value_type=float)


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription([
        DeclareLaunchArgument("gain", default_value="1.5"),       # ros2 launch ... gain:=4.0 처럼 바꾼다
        DeclareLaunchArgument("noise", default_value="0.0"),
        DeclareLaunchArgument("slip", default_value="0.0"),
        DeclareLaunchArgument("record", default_value=""),
        Node(package="point_robot", executable="sensor", output="screen",
             parameters=[{"noise": 실수_인자("noise")}]),
        Node(package="point_robot", executable="judge", output="screen",
             parameters=[{"gain": 실수_인자("gain")}]),
        Node(package="point_robot", executable="simulator", output="screen",
             parameters=[{"slip": 실수_인자("slip"), "record": LaunchConfiguration("record")}],
             on_exit=Shutdown()),                                  # 시뮬레이터가 끝나면 모두 끝낸다
    ])
