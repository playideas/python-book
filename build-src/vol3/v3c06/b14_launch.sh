# launch 파일 하나로 노드들을 띄운다. 화면이 없으니 RViz만 끄고(rviz:=false) tf를 확인한다
cd "$(dirname "$0")"
ros2 launch ./팔보기.launch.py rviz:=false > /dev/null 2>&1 &
sleep 4
ros2 node list
timeout 3 ros2 run tf2_ros tf2_echo base_link tip 2> /dev/null | grep -m1 "Translation"
kill %1
wait
