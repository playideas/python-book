echo "## std_msgs/msg/Float32"
ros2 interface show std_msgs/msg/Float32
echo "## geometry_msgs/msg/Twist"
ros2 interface show geometry_msgs/msg/Twist --no-comments
echo "## geometry_msgs/msg/PointStamped"
ros2 interface show geometry_msgs/msg/PointStamped --no-comments
echo "## 설치된 메시지 타입 수"
ros2 interface list --only-msgs | grep -c /msg/
