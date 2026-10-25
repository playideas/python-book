source /src/책환경.sh
source /src/인터페이스패키지.sh                     # MoveTo 타입을 만들어 빌드한다
echo "## 만든 액션 타입"
ros2 interface show robot_interfaces/action/MoveTo --no-comments
ros2 daemon start > /dev/null
뒤에서 python3 /src/이동서버.py
sleep 1
echo "## 액션 목록"
ros2 action list -t
echo "## 클라이언트"
python3 /src/이동클라이언트.py
kill -INT %1 && wait
