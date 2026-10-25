source /src/책환경.sh
source /src/패키지만들기.sh
패키지_만들기 point_robot 점로봇.py sensor=센서노드.py judge=판단노드.py simulator=시뮬레이터노드.py
for gain in 0.5 1.5 12.0; do                    # 이득만 바꿔 세 번 돌리고, 경로를 CSV로 남긴다
    echo "## 이득 $gain"
    ros2 launch /src/점로봇_launch.py gain:=$gain noise:=0.02 slip:=0.2 record:=path_gain_$gain.csv \
        | grep "^\[simulator" | sed 's/^\[simulator-3\] //' | tail -1
done
