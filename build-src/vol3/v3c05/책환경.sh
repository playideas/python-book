# 이 장의 실행 블록이 맨 위에서 불러오는 공통 설정
# 로그에서 실행마다 바뀌는 시각을 빼고 "[수준] [노드 이름]: 내용" 모양으로 찍는다
export RCUTILS_CONSOLE_OUTPUT_FORMAT="[{severity}] [{name}]: {message}"
# 로그를 print와 같은 표준 출력으로 보내고, print도 바로바로 내보내 순서가 섞이지 않게 한다
export RCUTILS_LOGGING_USE_STDOUT=1
export PYTHONUNBUFFERED=1

# 명령을 뒤에서 띄운다. 스크립트 속 뒤 작업은 Ctrl+C 신호(SIGINT)를 무시하도록 되어 있어서,
# 그 설정을 풀고 띄워야 나중에 kill -INT로 Ctrl+C를 누른 것처럼 깔끔하게 끝낼 수 있다
뒤에서() {
    python3 -c 'import os, signal, sys; signal.signal(signal.SIGINT, signal.SIG_DFL); os.execvp(sys.argv[1], sys.argv[1:])' "$@" &
}
