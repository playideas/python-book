source /src/책환경.sh
ros2 daemon start                                  # 명령줄 도구가 쓰는 도우미를 미리 띄운다
뒤에서 python3 /src/배터리구독.py > /tmp/구독.txt
뒤에서 ros2 topic pub -r 10 /battery_voltage std_msgs/msg/Float32 "{data: 12.4}" > /dev/null
sleep 2                                            # 서로 찾을 시간을 준다

echo "## 지금 떠 있는 노드"; ros2 node list
echo "## 토픽과 타입"; ros2 topic list -t
echo "## 토픽 하나 자세히"; ros2 topic info /battery_voltage
echo "## 메시지 하나 엿보기"; ros2 topic echo --once /battery_voltage
echo "## 1초에 몇 번 오나"
timeout -s INT 3 ros2 topic hz /battery_voltage > /tmp/hz.txt          # 3초 동안 재고
awk 'NR == 1 {printf "평균 %.0fHz\n", $3}' /tmp/hz.txt                 # 첫 줄의 평균만 반올림해 본다

kill -INT %2 && sleep 0.5                          # 10Hz 발행을 멈추고
ros2 topic pub --once /battery_voltage std_msgs/msg/Float32 "{data: 11.5}" > /dev/null   # 한 번만 보낸다
sleep 0.5
kill -INT %1 && wait
echo "## 구독 노드가 받은 마지막 두 메시지"; tail -2 /tmp/구독.txt
