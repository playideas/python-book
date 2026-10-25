# 3권 5~6장 예제용 ROS 2 Lyrical 환경 (맥·윈도우에서는 이 이미지로 실습한다)
FROM ros:lyrical-ros-base
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3-numpy \
        python3-scipy \
        ros-lyrical-robot-state-publisher \
        ros-lyrical-joint-state-publisher \
        ros-lyrical-tf2-ros-py \
        ros-lyrical-xacro \
        ros-lyrical-urdfdom-py \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /work
# 모든 셸에서 ROS 2 환경을 불러온다
RUN echo "source /opt/ros/lyrical/setup.bash" >> /root/.bashrc
ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
