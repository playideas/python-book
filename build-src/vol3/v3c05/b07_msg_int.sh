source /src/책환경.sh
echo "## 그냥 실행"
python3 /src/정수발행.py 2>&1 | sed 's/^python3: .*: Assertion/Assertion/'
echo "프로세스가 끝난 상태: ${PIPESTATUS[0]}"
echo "## 칸 검사를 켜고 실행"
ROS_PYTHON_CHECK_FIELDS=1 python3 /src/정수발행.py 2>&1 | tail -1
