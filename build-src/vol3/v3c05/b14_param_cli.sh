source /src/책환경.sh
ros2 daemon start > /dev/null
뒤에서 python3 /src/속도제한노드.py --ros-args -p max_speed:=0.3 > /tmp/노드.txt   # 시작할 때 값 주기
sleep 2

echo "## 파라미터 목록"; ros2 param list /speed_limiter
echo "## 읽기"; ros2 param get /speed_limiter max_speed
echo "## 바꾸기"; ros2 param set /speed_limiter max_speed 0.8
echo "## 너무 큰 값"; ros2 param set /speed_limiter max_speed 5.0 2>&1
echo "## 타입이 다른 값"; ros2 param set /speed_limiter max_speed fast 2>&1
echo "## 지금 값을 파일로"; ros2 param dump /speed_limiter > /tmp/설정.yaml && cat /tmp/설정.yaml

kill -INT %1 && wait
echo "## 노드의 로그"; cat /tmp/노드.txt
echo "## 시작할 때부터 너무 큰 값"
python3 /src/속도제한노드.py --ros-args -p max_speed:=2.0 2>&1 | tail -1
