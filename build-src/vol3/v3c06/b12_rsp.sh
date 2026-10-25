# 두관절팔.urdf로 robot_state_publisher와 joint_state_publisher를 띄우고 들여다본다
cd "$(dirname "$0")"
ros2 run robot_state_publisher robot_state_publisher \
    --ros-args -p robot_description:="$(cat 두관절팔.urdf)" > /dev/null 2>&1 &
ros2 run joint_state_publisher joint_state_publisher \
    --ros-args -p zeros.shoulder:=0.5236 -p zeros.elbow:=0.7854 > /dev/null 2>&1 &
sleep 3                                       # 노드들이 뜨고 서로 찾을 시간
echo "--- 노드 ---";  ros2 node list
echo "--- 토픽 ---";  ros2 topic list
echo "--- /joint_states 한 번 ---"
ros2 topic echo --once /joint_states --field name
ros2 topic echo --once /joint_states --field position
echo "--- tf2_echo base_link tip ---"
timeout 3 ros2 run tf2_ros tf2_echo base_link tip 2> /dev/null | grep -m1 -A8 "Translation"
kill %1 %2
