source /src/책환경.sh
뒤에서 python3 /src/배터리구독.py > /tmp/구독.txt    # 구독 노드를 뒤에서 띄워 두고
python3 /src/배터리발행.py > /tmp/발행.txt           # 발행 노드는 다섯 번 보내면 스스로 끝난다
sleep 1                                               # 마지막 메시지가 도착할 시간을 조금 준다
kill -INT %1 && wait                                  # 구독 노드에 Ctrl+C를 보낸다
echo "--- 발행 노드 ---" && cat /tmp/발행.txt
echo "--- 구독 노드 ---" && cat /tmp/구독.txt
