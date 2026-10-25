source /src/책환경.sh
source /src/패키지만들기.sh
패키지_만들기 point_robot 점로봇.py sensor=센서노드.py judge=판단노드.py simulator=시뮬레이터노드.py
ros2 launch /src/점로봇_launch.py | grep "^\[simulator" | sed 's/^\[simulator-3\] //'
