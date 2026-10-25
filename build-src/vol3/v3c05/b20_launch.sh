source /src/책환경.sh
source /src/패키지만들기.sh
패키지_만들기 battery_demo battery_publisher=배터리발행.py battery_monitor=배터리구독.py
ros2 daemon start > /dev/null
뒤에서 ros2 launch /src/배터리_launch.py > /tmp/launch.txt
sleep 3
echo "## 노드"; ros2 node list
echo "## 토픽"; ros2 topic list | grep battery
kill -INT %1 && wait                       # launch에 Ctrl+C를 보내면 띄운 노드를 모두 끝낸다
echo "## 감시 노드의 출력(노드별로 모아서)"
grep "^\[battery_monitor" /tmp/launch.txt | sort -s -k1,1
