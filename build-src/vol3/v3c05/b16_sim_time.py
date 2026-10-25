import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rosgraph_msgs.msg import Clock
from rclpy.time import Time

with rclpy.init():
    # 시뮬레이터 흉내: /clock 토픽으로 '지금 시뮬레이션 시각'을 알린다
    시계_노드 = Node("fake_simulator")
    시계_발행자 = 시계_노드.create_publisher(Clock, "/clock", 10)

    # use_sim_time을 켠 노드: 벽시계 대신 /clock을 시계로 쓴다
    제어_노드 = Node("controller", parameter_overrides=[Parameter("use_sim_time", value=True)])
    제어_노드.create_timer(1.0, lambda: print(f"타이머: 시뮬레이션 시각 {제어_노드.get_clock().now().nanoseconds / 1e9:.1f}초"))

    실행기 = rclpy.executors.SingleThreadedExecutor()
    실행기.add_node(시계_노드)
    실행기.add_node(제어_노드)
    for _ in range(20):
        실행기.spin_once(timeout_sec=0.05)
    for 걸음 in range(1, 36):               # 시뮬레이션 시간을 0.1초씩 3.5초까지 흘린다
        시계_발행자.publish(Clock(clock=Time(nanoseconds=걸음 * 100_000_000).to_msg()))
        for _ in range(3):
            실행기.spin_once(timeout_sec=0.01)
    print("제어 노드의 시각:", 제어_노드.get_clock().now().nanoseconds / 1e9, "초")
    print("시계 노드의 시각:", 시계_노드.get_clock().now().nanoseconds / 1e9 > 1e9, "(벽시계: 1970년부터 센 초)")
