from geometry_msgs.msg import Point, Twist
from std_msgs.msg import Float32

# 메시지는 칸(필드)이 정해진 파이썬 객체다
속도 = Twist()                       # 모든 칸이 0으로 시작한다
속도.linear.x = 0.3                  # 앞으로 0.3m/s
속도.angular.z = 0.5                 # 왼쪽으로 0.5rad/s 돌며
print(속도)
print("칸과 타입:", Twist.get_fields_and_field_types())

목표 = Point(x=2.0, y=1.0)            # 만들면서 칸을 채울 수도 있다
print(목표)

전압 = Float32(data=12.4)
print("파이썬 안에서:", 전압.data)    # 보내기 전에는 파이썬 float(64비트) 그대로다
