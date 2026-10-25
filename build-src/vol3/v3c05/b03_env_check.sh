echo "ROS 2 배포판: $ROS_DISTRO"
python3 --version
python3 -c "import rclpy.utilities as u; print('통신 미들웨어:', u.get_rmw_implementation_identifier())"
ros2 pkg list | wc -l | xargs echo "설치된 패키지 수:"
