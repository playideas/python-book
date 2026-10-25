from geometry_msgs.msg import PointStamped
from rclpy.clock import ClockType
from rclpy.time import Time

# 카메라가 시각 12.4초에 찍은 사진에서 컵을 찾았다. 처리에 시간이 걸려 12.7초에 판단 노드에 도착했다
메시지 = PointStamped()
메시지.header.stamp = Time(seconds=12, nanoseconds=400_000_000).to_msg()   # 언제 잰 값인가
메시지.header.frame_id = "camera"                                          # 어느 좌표계로 잰 값인가
메시지.point.x, 메시지.point.y, 메시지.point.z = 0.1, -0.05, 0.8
print(메시지.header)

# 노드 안이라면 self.get_clock().now()로 받는 '지금'. 그 시계와 같은 종류(ROS_TIME)로 만든다
지금 = Time(seconds=12, nanoseconds=700_000_000, clock_type=ClockType.ROS_TIME)
늦음 = 지금 - Time.from_msg(메시지.header.stamp)           # 시각 - 시각 = 시간 간격(Duration)
print(f"이 측정은 {늦음.nanoseconds / 1e9:.1f}초 전의 세상이다")
