# 같은 상자 안에서 ROS_DOMAIN_ID만 바꿔 보기: 받는 쪽은 늘 도메인 1, 보내는 쪽은 1과 2
source /opt/ros/lyrical/setup.bash
for sender in 1 2; do
    ROS_DOMAIN_ID=1 timeout -k 1 8 ros2 topic echo --once /chatter std_msgs/msg/String > /tmp/got.txt 2>/dev/null &
    sleep 2
    ROS_DOMAIN_ID=$sender timeout -k 1 5 ros2 topic pub -r 5 /chatter std_msgs/msg/String \
        "{data: '도메인 $sender에서 보냄'}" > /dev/null 2>&1
    wait
    got=$(grep "^data:" /tmp/got.txt || echo "(아무것도 받지 못함)")
    echo "받는 쪽 도메인 1, 보내는 쪽 도메인 $sender → $got"
done
