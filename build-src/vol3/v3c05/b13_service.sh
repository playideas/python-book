source /src/책환경.sh
뒤에서 python3 /src/모터서버.py > /tmp/서버.txt
python3 /src/모터스위치.py                                   # 파이썬 클라이언트로 세 번 요청

echo "## 명령줄에서"
ros2 service list | grep motor                                # 서비스 목록에서 찾기
ros2 service type /enable_motor
ros2 interface show std_srvs/srv/SetBool
ros2 service call /enable_motor std_srvs/srv/SetBool "{data: true}" | tail -2   # 응답 부분만

kill -INT %1 && wait
echo "## 서버의 로그"; cat /tmp/서버.txt
