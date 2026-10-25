source /src/책환경.sh
source /src/패키지만들기.sh
패키지_만들기 battery_demo battery_publisher=배터리발행.py battery_monitor=배터리구독.py

echo "## 패키지 폴더"
cd /tmp/ws/src && find battery_demo -type f -not -path "*/test/*" | sort
echo "## 진입점(setup.py의 일부)"
grep -A3 "console_scripts" battery_demo/setup.py
echo "## 의존 패키지(package.xml의 일부)"
grep "<depend>" battery_demo/package.xml
echo "## 빌드 기록(걸린 시간은 지웠다)"
sed -E 's/ \[[0-9.]+s\]//' /tmp/빌드.txt
echo "## 작업 공간"
ls /tmp/ws
echo "## 이 패키지의 실행 파일"
ros2 pkg executables battery_demo
echo "## ros2 run으로 실행"
뒤에서 ros2 run battery_demo battery_monitor > /tmp/감시.txt
ros2 run battery_demo battery_publisher > /dev/null
sleep 1 && kill -INT %1 && wait
cat /tmp/감시.txt
