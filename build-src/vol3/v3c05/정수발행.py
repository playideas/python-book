"""5.3절: 실수(float64) 칸에 정수 1을 넣고 발행해 보는 실험."""
import rclpy
from geometry_msgs.msg import Twist

with rclpy.init():
    노드 = rclpy.create_node("int_test")
    발행자 = 노드.create_publisher(Twist, "cmd_vel", 10)
    속도 = Twist()
    속도.linear.x = 1                   # 1.0이 아니라 정수 1
    print("넣기는 됐다:", repr(속도.linear.x))
    발행자.publish(속도)
    print("발행도 됐다")
