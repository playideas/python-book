# 컨테이너 안의 ROS 2 환경과 Dockerfile에서 더한 패키지의 판 번호
source /opt/ros/lyrical/setup.bash
echo "우분투 $(. /etc/os-release && echo $VERSION_ID), ROS 2 $ROS_DISTRO, $(python3 --version)"
echo "ROS_DOMAIN_ID: ${ROS_DOMAIN_ID:-(정하지 않음, 0으로 동작)}"
dpkg-query -W -f='${Package} ${Version}\n' python3-numpy python3-scipy \
    ros-lyrical-robot-state-publisher ros-lyrical-joint-state-publisher ros-lyrical-tf2-ros-py \
    ros-lyrical-xacro ros-lyrical-urdfdom-py | awk '{printf "  %-36s %s\n", $1, $2}'
