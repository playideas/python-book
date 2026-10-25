# Chapter 5. ROS 2 기초: 로봇 프로그램을 여러 조각으로

> **학습 목표**  
> - 프로그램 하나에 모든 일을 넣은 로봇의 문제를 알고, 역할별 노드가 메시지를 주고받는 ROS 2의 구조 설명하기
> - Docker로 ROS 2 Lyrical 환경을 띄우고, rclpy로 노드·타이머·로거를 써서 첫 노드 만들기
> - 토픽으로 메시지를 발행·구독하고, 메시지 타입과 `ros2` 명령줄 도구로 들여다보기
> - QoS(신뢰성·기록 깊이·지속성)가 연결과 전달을 어떻게 바꾸는지 실행으로 확인하기
> - 서비스·액션·파라미터를 언제 쓰는지 구분하고 직접 만들어 보기
> - 실행기와 타이머, 메시지의 시각, 시뮬레이션 시간을 1장의 제어 주기와 연결하기
> - 노드를 패키지로 묶어 빌드하고, launch 파일로 여러 노드를 한 번에 띄우기
> - 1장의 점 로봇을 감지·판단·행동 세 노드로 나눠 잇고, 이득을 바꿔 가며 결과 비교하기

---

## 들어가며: 프로그램 하나에 다 넣으면 무엇이 문제일까요?

1장 1.1절에서 점 로봇을 `고리로봇` 클래스로 다시 짜면서 감지·판단·행동을 메서드 셋으로 나눴죠. 그때 "센서를 바꾸면 `감지`만 고치면 된다"고 했습니다. 그런데 진짜 로봇이 되면 이야기가 달라집니다. 감지에는 카메라 사진에서 물체를 찾는 무거운 계산이 들어가고, 행동에는 0.01초마다 꼬박꼬박 모터에 명령을 보내는 일이 들어가요. 둘을 한 프로그램의 한 고리에 넣으면 어떻게 될까요? 카메라 처리에 0.05초가 걸린다고 하고, 걸린 시간을 직접 더해 가며 흉내 내 보겠습니다.

```python
# 프로그램 하나에 카메라 처리와 모터 명령을 함께 넣은 로봇(시계는 걸린 시간을 직접 더해 센다)
모터_주기 = 0.01            # 모터 명령은 0.01초(100Hz)마다 보내야 한다
카메라_처리_시간 = 0.05     # 사진 한 장에서 물체를 찾는 데 0.05초 걸린다

시각 = 0.0
명령_시각들 = []
try:
    for 사진_번호 in range(1, 100):
        시각 += 카메라_처리_시간                    # 감지: 사진 처리가 끝나야
        if 사진_번호 == 4:
            raise ValueError("4번째 사진이 깨져 있다")
        명령_시각들.append(round(시각, 2))          # 판단·행동: 모터 명령을 보낼 수 있다
except ValueError as 오류:
    print(f"{시각:.2f}초: {오류} → 프로그램 전체가 멈췄다")

간격들 = [round(b - a, 2) for a, b in zip(명령_시각들, 명령_시각들[1:])]
print("모터 명령을 보낸 시각:", 명령_시각들)
print(f"명령 사이 간격: {간격들} (보내야 하는 간격은 {모터_주기}초)")
```

```text
0.20초: 4번째 사진이 깨져 있다 → 프로그램 전체가 멈췄다
모터 명령을 보낸 시각: [0.05, 0.1, 0.15]
명령 사이 간격: [0.05, 0.05] (보내야 하는 간격은 0.01초)
```

문제가 두 가지 보입니다. 첫째, 모터 명령이 0.01초가 아니라 0.05초마다 나갔어요. 사진 처리가 끝나야 고리가 다음으로 넘어가니, 가장 느린 일이 가장 급한 일의 박자를 정해 버린 거예요. 1장 1.4절에서 박자가 느려지면 로봇이 목표를 지나치고 흔들리는 것을 봤죠. 둘째, 4번째 사진 하나가 깨졌을 뿐인데 **프로그램 전체**가 멈췄습니다. 카메라 쪽 오류 때문에 모터 명령까지 끊긴 거예요. 달리던 로봇이라면 큰일입니다.

문제가 하나 더 있어요. 라이다 회사가 준 드라이버, 선배가 짠 경로 계획, 내가 짠 판단 코드를 한 프로그램에 섞으려면 서로의 코드 안쪽까지 알아야 하고, 부품 하나 바꿀 때마다 전체를 손봐야 합니다.

해결책은 의외로 단순합니다. **일을 역할별로 나눠 따로 도는 프로그램으로 만들고, 프로그램끼리 메시지를 주고받게** 하는 거예요. 방송국을 떠올려 보세요. 방송국은 누가 듣는지 모른 채 정해진 주파수로 소식을 내보내고, 라디오는 주파수만 맞추면 들을 수 있습니다. 듣는 사람이 늘거나 줄어도 방송국은 신경 쓰지 않고, 라디오 하나가 고장 나도 방송은 계속돼요. 카메라 프로그램은 "물체 위치" 채널로 소식을 내보내고, 모터 프로그램은 자기 박자대로 돌다가 새 소식이 오면 반영하면 됩니다. 카메라 프로그램이 죽어도 모터 프로그램은 살아서 로봇을 세울 수 있어요.

이렇게 역할별로 나뉜 프로그램을 **노드(node)**, 노드들이 소식을 주고받는 이름 붙은 채널을 **토픽(topic)**, 오가는 소식 한 건을 **메시지(message)** 라고 부릅니다. 이 구조를 표준으로 만들고 그에 필요한 도구를 모아 둔 것이 이 장에서 배울 **ROS 2**예요. 이 장에서는 노드를 만들고, 토픽·서비스·액션으로 잇고, 설정을 파라미터로 바꾸고, 여러 노드를 한 번에 띄우는 방법을 차례로 익힙니다. 마지막에는 1장의 점 로봇을 감지·판단·행동 세 노드로 나눠 직접 이어 봅니다.

> **Q. ROS 2를 꼭 써야 로봇을 만들 수 있나요?**
> 아닙니다. 작은 로봇은 파이썬 프로그램 하나로도 충분히 돌아가요. 하지만 센서와 모터가 늘고 여러 사람이 함께 만들기 시작하면 이 장에서 볼 문제들이 금방 생기고, 그때 바퀴를 다시 발명하지 않게 해 주는 것이 ROS 2입니다. 연구실과 회사의 로봇 소프트웨어 대부분이 ROS 2 위에서 만들어지고, 공개된 로봇 패키지도 대부분 ROS 2용이라 한 번 익혀 두면 쓸 곳이 많아요. 이 장의 예제는 Docker 안의 ROS 2 Lyrical(파이썬 3.14)에서 실행해 확인했습니다.

## 5.1 ROS 2는 무엇이고 무엇이 아닌가

### 운영 체제가 아니라 약속과 도구 모음

ROS는 Robot Operating System의 줄임말이지만, 윈도우나 리눅스 같은 **운영 체제가 아닙니다**. ROS 2는 리눅스(주로 우분투) 위에서 도는 보통 프로그램과 라이브러리의 모음이에요. 크게 세 가지를 줍니다.

1. **통신**: 노드끼리 메시지를 주고받는 방법. 토픽, 서비스, 액션, 파라미터가 여기에 속합니다
2. **도구**: 노드와 메시지를 들여다보는 `ros2` 명령, 여러 노드를 한 번에 띄우는 launch, 패키지를 빌드하는 colcon, 메시지를 녹화하고 다시 트는 `ros2 bag`, 시각화 도구 RViz
3. **생태계**: 센서 드라이버, 좌표 변환, 경로 계획, 팔 제어처럼 다른 사람이 만들어 공개한 수많은 패키지

이 장에서 파이썬으로 노드를 만들 때 쓰는 라이브러리는 **rclpy**(ROS Client Library for Python)입니다. C++로 만들 때는 rclcpp를 쓰는데, 두 언어로 만든 노드도 같은 토픽으로 아무 문제 없이 이야기를 나눠요.

이름의 2는 통신 부분부터 새로 설계한 두 번째 판이라는 뜻입니다. 처음 ROS(ROS 1)의 마지막 판 Noetic은 2025년 5월에 지원이 끝났으니, 새로 시작한다면 ROS 2를 배우면 됩니다.

### 배포판과 Lyrical Luth

ROS 2는 해마다 5월에 새 **배포판(distribution)** 을 냅니다. 이름은 알파벳 순서로 붙고, 짝수 해에 나오는 판은 오래 지원하는 **LTS** 판이에요.

| 배포판 | 나온 때 | 우분투 | 비고 |
|---|---|---|---|
| Humble Hawksbill | 2022년 5월 | 22.04 | LTS |
| Jazzy Jalisco | 2024년 5월 | 24.04 | LTS |
| Kilted Kaiju | 2025년 5월 | 24.04 | 짧게 지원 |
| Lyrical Luth | 2026년 5월 | 26.04 | LTS, 이 책에서 쓰는 판 |

이 책은 가장 새 LTS인 **Lyrical Luth**를 씁니다. 배포판마다 우분투 판과 파이썬 판이 짝지어져 있어서, Lyrical은 우분투 26.04의 파이썬 3.14를 씁니다. 다른 배포판에서도 이 장의 코드는 대부분 그대로 돌지만, 판이 바뀌며 달라진 작은 부분(예를 들어 로거의 `warn`이 사라지고 `warning`만 남은 것)이 있으니 오류가 나면 배포판부터 확인하세요.

### DDS: 중앙 우체국이 없는 통신

노드끼리 서로를 어떻게 찾을까요? ROS 1에는 `roscore`라는 중앙 관리 프로그램이 있어서, 이것이 죽으면 새 연결을 못 만들었어요. ROS 2는 **DDS(Data Distribution Service)** 라는 산업용 통신 표준을 밑에 깔았습니다. DDS에서는 노드가 같은 네트워크에 "누구 있어요?" 하고 알리며 서로를 저절로 찾아요(이것을 **디스커버리**라고 합니다). 중앙 우체국이 없으니 아무 노드나 먼저 떠도 되고, 같은 컴퓨터든 같은 네트워크의 다른 컴퓨터든 똑같이 연결됩니다. DDS 구현은 여러 가지가 있고, ROS 2는 그 위에 **RMW**(ROS MiddleWare)라는 얇은 층을 두어 어느 것이든 같은 방식으로 쓰게 했어요. 같은 네트워크의 다른 컴퓨터뿐 아니라 한 컴퓨터에 띄운 Docker 컨테이너 여러 개도 서로의 노드와 토픽이 보입니다. 여러 사람이 실습하거나 실험 두 개를 따로 돌릴 때 섞이지 않게 하려면 환경 변수 `ROS_DOMAIN_ID`에 서로 다른 번호(기본값 0)를 주면 됩니다.

### Docker로 Lyrical 띄우기

ROS 2는 우분투에서 가장 잘 돌아갑니다. 1장 1.6절에서 약속한 대로, 맥과 윈도우에서는 **Docker** 컨테이너 안에 우분투와 ROS 2를 담아 실습해요. 컨테이너는 내 컴퓨터 안에 띄우는 가벼운 리눅스 상자예요. Docker Desktop 설치와 자주 쓰는 명령은 부록에 정리해 두었습니다. 상자의 설계도인 `examples/vol3/ros/Dockerfile`은 이렇게 생겼어요.

```dockerfile
# 3권 5~6장 예제용 ROS 2 Lyrical 환경 (맥·윈도우에서는 이 이미지로 실습한다)
FROM ros:lyrical-ros-base
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3-numpy \
        python3-scipy \
        ros-lyrical-robot-state-publisher \
        ros-lyrical-joint-state-publisher \
        ros-lyrical-tf2-ros-py \
        ros-lyrical-xacro \
        ros-lyrical-urdfdom-py \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /work
# 모든 셸에서 ROS 2 환경을 불러온다
RUN echo "source /opt/ros/lyrical/setup.bash" >> /root/.bashrc
ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
```

ROS 2 공식 이미지 `ros:lyrical-ros-base`에서 출발해 NumPy, SciPy와 6장에서 쓸 패키지 몇 개를 더 설치합니다. 이미지를 만들고 컨테이너에 들어가는 명령은 이렇습니다.

```bash
# 저장소의 examples/vol3 폴더에서 한다(맥·윈도우·리눅스 모두 같다)
docker build -t python-book-ros:lyrical ros       # 이미지 만들기. 처음 한 번만, 몇 분 걸린다
cd 05-ros2-basics
# 이 장 폴더를 컨테이너의 /src에 연결하고, /src에서 시작하는 셸로 들어간다
docker run -it --rm -v "$PWD":/src -w /src python-book-ros:lyrical
```

`-v "$PWD":/src`는 내 컴퓨터의 장 폴더를 컨테이너 안의 `/src`로 연결합니다. 컨테이너 안에서 `/src`에 파일을 쓰면 내 컴퓨터의 폴더에 그대로 남아요. `-w /src`는 그 폴더에서 시작하라는 뜻, `-it`는 키보드로 명령을 칠 수 있게, `--rm`은 나올 때 상자를 지우라는 뜻입니다. 터미널을 하나 더 쓰려면 `docker exec -it <컨테이너 이름> bash`로 같은 상자에 들어가요.

컨테이너에 들어왔으면 환경부터 확인해 봅시다.

```bash
echo "ROS 2 배포판: $ROS_DISTRO"
python3 --version
python3 -c "import rclpy.utilities as u; print('통신 미들웨어:', u.get_rmw_implementation_identifier())"
ros2 pkg list | wc -l | xargs echo "설치된 패키지 수:"
```

```text
ROS 2 배포판: lyrical
Python 3.14.4
통신 미들웨어: rmw_fastrtps_cpp
설치된 패키지 수: 197
```

배포판은 Lyrical, 파이썬은 3.14입니다. 맥에서 `uv`로 쓰던 파이썬 3.12와는 **다른 파이썬**이라는 점에 주의하세요. 컨테이너 안의 NumPy도 우분투가 준 판(2.3)이라 1~4장의 환경과 다릅니다. 통신 미들웨어는 Fast DDS(`rmw_fastrtps_cpp`)이고, 기본 이미지에 들어 있는 ROS 패키지가 197개 있어요.

이 장의 코드 블록은 두 종류입니다. 파이썬 블록은 컨테이너 안에서 `python3`로, 셸 블록은 컨테이너 안의 bash에서 실행한 결과예요. 장 폴더는 어디서 실행해도 되도록 `/src/첫노드.py`처럼 전체 경로로 적었습니다. 실습의 그림을 그리는 블록 하나만 맥에서 실행합니다.

## 5.2 첫 번째 노드

### 노드는 일꾼 한 명

노드는 한 가지 일을 맡은 일꾼입니다. 일꾼이 하는 일은 대개 둘 중 하나예요. **정해진 박자마다** 무언가를 하거나(센서 읽기, 모터 명령), **소식이 오면** 반응하거나(메시지 처리). 두 경우 모두 "이때가 되면 이 함수를 불러 줘"라고 맡겨 두는 방식으로 짭니다. 식당에서 진동벨을 받아 두고 자리에 앉아 있으면 음식이 나왔을 때 벨이 울리는 것과 같아요. 이렇게 맡겨 두는 함수를 **콜백(callback)** 이라고 합니다.

0.5초마다 박자를 세는 노드를 만들어 보겠습니다. ROS 2 노드는 rclpy의 `Node` 클래스를 물려받아 만들어요.

```python
"""5.2절: 0.5초마다 박자를 세는 첫 번째 노드."""
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class 첫노드(Node):
    def __init__(self):
        super().__init__("first_node")                      # ROS 안에서 부르는 이름
        self.박자 = 0
        self.타이머 = self.create_timer(0.5, self.박자_세기)  # 0.5초마다 박자_세기를 부른다
        self.get_logger().info("노드를 시작했다")

    def 박자_세기(self) -> None:
        self.박자 += 1
        self.get_logger().info(f"{self.박자}번째 박자")
        if self.박자 == 3:                                   # 책에서는 세 박자만 세고 끝낸다
            self.get_logger().info("세 박자를 셌으니 끝낸다")
            rclpy.shutdown()


def main() -> None:
    try:
        with rclpy.init():            # ROS 2 통신을 준비하고, 블록을 나갈 때 정리한다
            노드 = 첫노드()
            rclpy.spin(노드)          # 타이머·메시지가 올 때마다 콜백을 불러 주며 기다린다
    except (KeyboardInterrupt, ExternalShutdownException):
        pass                          # Ctrl+C나 바깥의 종료 요청은 정상 종료로 본다


if __name__ == "__main__":
    main()
```

- `super().__init__("first_node")`: 노드에 ROS 안에서 쓸 이름을 붙입니다. 다른 노드와 명령줄 도구가 이 이름으로 찾아요.
- `create_timer(0.5, self.박자_세기)`: 0.5초마다 `박자_세기`를 불러 달라고 맡겨 둡니다. 1장 1.4절에서 `다음_박자`를 계산하며 직접 돌렸던 메트로놈을 ROS가 대신 돌려 주는 거예요.
- `get_logger().info(...)`: `print` 대신 쓰는 로그입니다. 어느 노드가 남긴 말인지, 얼마나 중요한지(INFO, WARN, ERROR 등)가 함께 찍혀요.
- `with rclpy.init():`: ROS 2 통신을 준비하고, 블록을 나갈 때 깔끔히 정리합니다.
- `rclpy.spin(노드)`: 타이머나 메시지가 올 때까지 기다렸다가 맡겨 둔 콜백을 부르기를 끝없이 되풀이합니다. 진동벨을 들고 기다리는 시간이에요.

보통 노드는 Ctrl+C를 누를 때까지 영원히 돕니다. 그러면 `spin` 안에서 `KeyboardInterrupt`가 나는데, `main`에서 이것을 정상 종료로 받아 줍니다. 책에서는 출력이 끝나야 하니 세 박자 뒤 `rclpy.shutdown()`으로 스스로 끝내게 했어요.

실행하기 전에 이 장의 셸 블록이 맨 위에서 불러올 설정 파일을 하나 보겠습니다.

```bash
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
```

ROS 2 로그는 원래 `[INFO] [1792723499.124885630] [first_node]: ...`처럼 1970년부터 센 초를 함께 찍어서 실행할 때마다 달라집니다. 책에서는 이 시각을 빼고 보이려고 출력 모양을 바꿨어요. 나머지 설정은 여러 노드의 출력이 섞이지 않게 하는 장치이고, 마지막 `뒤에서` 함수는 5.3절에서 노드를 뒤에서 띄울 때 씁니다. 직접 따라 할 때는 이 파일을 불러오지 않아도 결과는 같고 로그에 시각만 더 붙습니다.

```bash
source /src/책환경.sh
python3 /src/첫노드.py
```

```text
[INFO] [first_node]: 노드를 시작했다
[INFO] [first_node]: 1번째 박자
[INFO] [first_node]: 2번째 박자
[INFO] [first_node]: 3번째 박자
[INFO] [first_node]: 세 박자를 셌으니 끝낸다
```

0.5초 간격으로 세 박자를 세고 끝났습니다. 로그 한 줄은 `[수준] [노드 이름]: 내용` 모양이에요. 노드가 수십 개로 늘어나면 이 노드 이름 덕분에 누가 한 말인지 바로 알 수 있습니다.

> **Q. `while True:`로 직접 고리를 돌리면 안 되나요?**
> 타이머가 하나뿐이라면 그래도 됩니다. 하지만 노드는 보통 타이머 여러 개와 메시지 여러 종류를 동시에 기다려요. 0.01초마다 모터 명령을 보내면서 언제 올지 모르는 카메라 메시지도 받아야 하죠. `spin`은 이런 기다림을 한꺼번에 처리하고, 할 일이 생긴 콜백만 골라 불러 줍니다. 직접 짜려면 꽤 복잡한 일이라 맡기는 편이 낫습니다. `spin`이 콜백을 어떤 순서로, 몇 개씩 부르는지는 5.7절에서 봅니다.

## 5.3 토픽: 발행하고 구독하기

### 방송국과 라디오

들어가며의 방송국 비유를 ROS 2의 말로 바꾸면 이렇습니다. 방송국은 **발행자(publisher)**, 라디오는 **구독자(subscriber)**, 주파수는 **토픽 이름**이에요. 발행자는 토픽에 메시지를 내보내기만 하고 누가 듣는지 신경 쓰지 않습니다. 구독자는 토픽 이름만 알면 받을 수 있어요. 한 토픽에 발행자와 구독자가 몇이든 붙을 수 있습니다.

단, 주파수만 맞으면 되는 라디오와 달리 토픽에는 하나가 더 맞아야 합니다. **메시지 타입**이에요. 메시지는 칸(필드)이 정해진 양식이라서, 발행자와 구독자가 같은 양식을 써야 서로의 말을 알아듣습니다.

### 메시지 타입 살펴보기

메시지 양식은 `ros2 interface show`로 볼 수 있습니다. 자주 쓰는 세 가지를 보겠습니다.

```bash
echo "## std_msgs/msg/Float32"
ros2 interface show std_msgs/msg/Float32
echo "## geometry_msgs/msg/Twist"
ros2 interface show geometry_msgs/msg/Twist --no-comments
echo "## geometry_msgs/msg/PointStamped"
ros2 interface show geometry_msgs/msg/PointStamped --no-comments
echo "## 설치된 메시지 타입 수"
ros2 interface list --only-msgs | grep -c /msg/
```

```text
## std_msgs/msg/Float32
# This was originally provided as an example message.
# It is deprecated as of Foxy
# It is recommended to create your own semantically meaningful message.
# However if you would like to continue using this please use the equivalent in example_msgs.

float32 data
## geometry_msgs/msg/Twist
Vector3  linear
	float64 x
	float64 y
	float64 z
Vector3  angular
	float64 x
	float64 y
	float64 z
## geometry_msgs/msg/PointStamped
std_msgs/Header header
	builtin_interfaces/Time stamp
		int32 sec
		uint32 nanosec
	string frame_id
Point point
	float64 x
	float64 y
	float64 z
## 설치된 메시지 타입 수
172
```

`std_msgs/msg/Float32`는 실수 하나(`data`)만 담는 가장 단순한 메시지입니다. 이름은 `패키지/msg/타입` 모양이에요. 주석을 보면 이런 단순한 메시지는 예제용이니 실제로는 **뜻이 드러나는 메시지**를 쓰라고 권하죠. 실수 하나만으로는 전압인지 온도인지 알 수 없으니까요. 실제 로봇의 배터리라면 `sensor_msgs/msg/BatteryState`를 씁니다. 이 장에서는 익히기 쉽게 `Float32`를 써요.

`geometry_msgs/msg/Twist`는 속도 명령에 쓰는 표준 메시지예요. `linear`(직선 속도, m/s)와 `angular`(회전 속도, rad/s)가 각각 x, y, z 세 칸을 가진 `Vector3`입니다. 2장의 몸 좌표 약속(x 앞, y 왼쪽, z 위)을 따르니, `linear.x`는 앞으로 가는 속도이고 `angular.z`는 왼쪽으로 도는 속도예요.

`geometry_msgs/msg/PointStamped`는 점 하나에 **머리말(`header`)** 이 붙은 메시지입니다. 머리말에는 언제 잰 값인지(`stamp`)와 어느 좌표계로 잰 값인지(`frame_id`)가 들어가요. 2장의 "이름에 기준을 적는 습관"을 메시지 안에 적어 보내는 셈이고, 이름 끝에 `Stamped`가 붙은 메시지는 모두 이 머리말을 가집니다. 이 이미지에 설치된 메시지 타입은 172개예요.

### 파이썬에서 메시지 다루기

파이썬에서 메시지는 칸이 정해진 객체입니다. 만들고, 칸을 채우고, 찍어 볼게요.

```python
from geometry_msgs.msg import Point, Twist
from std_msgs.msg import Float32

# 메시지는 칸(필드)이 정해진 파이썬 객체다
속도 = Twist()                       # 모든 칸이 0으로 시작한다
속도.linear.x = 0.3                  # 앞으로 0.3m/s
속도.angular.z = 0.5                 # 왼쪽으로 0.5rad/s 돌며
print(속도)
print("칸과 타입:", Twist.get_fields_and_field_types())

목표 = Point(x=2.0, y=1.0)            # 만들면서 칸을 채울 수도 있다
print(목표)

전압 = Float32(data=12.4)
print("파이썬 안에서:", 전압.data)    # 보내기 전에는 파이썬 float(64비트) 그대로다
```

```text
geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=0.3, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0.0, y=0.0, z=0.5))
칸과 타입: {'linear': 'geometry_msgs/Vector3', 'angular': 'geometry_msgs/Vector3'}
geometry_msgs.msg.Point(x=2.0, y=1.0, z=0.0)
파이썬 안에서: 12.4
```

빈 메시지를 만들면 모든 칸이 0으로 채워져 있고, 점(`.`)으로 칸을 찾아 값을 넣습니다. 만들면서 `Point(x=2.0, y=1.0)`처럼 채울 수도 있어요. 마지막 줄을 기억해 두세요. `Float32`에 12.4를 넣었는데 파이썬 안에서는 12.4 그대로입니다. 32비트 실수로 바뀌는 건 보낼 때예요. 이 차이는 조금 뒤 명령줄 도구에서 다시 봅니다.

메시지 칸에 값을 넣을 때 꼭 알아야 할 함정이 하나 있습니다. 실수 칸(`float64`)에 정수 `1`을 넣으면 어떻게 될까요?

```python
"""5.3절: 실수(float64) 칸에 정수 1을 넣고 발행해 보는 실험."""
import rclpy
from geometry_msgs.msg import Twist

with rclpy.init():
    노드 = rclpy.create_node("int_test")
    발행자 = 노드.create_publisher(Twist, "cmd_vel", 10)
    속도 = Twist()
    속도.linear.x = 1                   # 1.0이 아니라 정수 1
    print("넣기는 됐다:", repr(속도.linear.x))
    발행자.publish(속도)
    print("발행도 됐다")
```

```bash
source /src/책환경.sh
echo "## 그냥 실행"
python3 /src/정수발행.py 2>&1 | sed 's/^python3: .*: Assertion/Assertion/'
echo "프로세스가 끝난 상태: ${PIPESTATUS[0]}"
echo "## 칸 검사를 켜고 실행"
ROS_PYTHON_CHECK_FIELDS=1 python3 /src/정수발행.py 2>&1 | tail -1
```

```text
## 그냥 실행
넣기는 됐다: 1
Assertion `PyFloat_Check(field)' failed.
프로세스가 끝난 상태: 134
## 칸 검사를 켜고 실행
AssertionError: The 'x' field must be of type 'float'
```

넣을 때는 아무 말이 없었는데, 발행하는 순간 프로세스가 **오류 한 줄만 남기고 통째로 죽었습니다**(끝난 상태 134는 강제 종료라는 뜻). "발행도 됐다"는 끝내 찍히지 않았고, 파이썬 예외가 아니라 `try`로 잡을 수도 없어요. ROS 2는 속도를 위해 넣을 때 타입을 검사하지 않고, 보낼 때 C 코드가 그제야 실수가 아닌 것을 발견하기 때문입니다. 환경 변수 `ROS_PYTHON_CHECK_FIELDS=1`을 켜면 넣는 순간 파이썬 예외로 알려 줍니다. 개발할 때는 이 변수를 켜 두고, 실수 칸에는 늘 `1.0`처럼 소수점을 찍어 넣는 습관을 들이세요. 실습의 노드에서 `float(...)`로 감싸서 넣는 것도 이 때문입니다.

### 발행자와 구독자

이제 노드 둘이 토픽으로 이야기하게 해 봅시다. 하나는 배터리 전압을 0.2초마다 발행하고, 하나는 그것을 구독해 전압이 낮으면 경고합니다.

```python
"""5.3절: 배터리 전압을 0.2초마다 발행하는 노드(전압은 예제용으로 만든 값)."""
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Float32


class 배터리발행(Node):
    def __init__(self):
        super().__init__("battery_publisher")
        self.발행자 = self.create_publisher(Float32, "battery_voltage", 10)   # 타입, 토픽 이름, 큐 깊이
        self.보낸_수 = 0
        self.create_timer(0.2, self.보내기)

    def 보내기(self) -> None:
        if self.발행자.get_subscription_count() == 0:      # 아무도 안 듣고 있으면 기다린다
            return
        메시지 = Float32()
        메시지.data = 12.5 - 0.2 * self.보낸_수              # 예제용: 한 번에 0.2V씩 떨어진다
        self.발행자.publish(메시지)
        self.get_logger().info(f"보냄: {메시지.data:.1f}V")
        self.보낸_수 += 1
        if self.보낸_수 == 5:                               # 책에서는 다섯 번만 보내고 끝낸다
            rclpy.shutdown()


def main() -> None:
    try:
        with rclpy.init():
            rclpy.spin(배터리발행())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == "__main__":
    main()
```

`create_publisher(Float32, "battery_voltage", 10)`이 발행자를 만듭니다. 메시지 타입, 토픽 이름, 그리고 **큐 깊이** 10이에요. 큐 깊이는 미처 보내지 못한 메시지를 몇 개까지 쌓아 둘지인데, 5.4절에서 자세히 봅니다. `get_subscription_count()`는 지금 이 토픽을 듣는 구독자 수예요. 듣는 이가 없을 때 보낸 메시지는 그냥 사라지니, 책의 결과가 매번 같도록 구독자가 생길 때까지 기다렸다가 보내게 했습니다. 진짜 센서 노드라면 듣는 이가 있든 없든 그냥 보냅니다.

```python
"""5.3절: 배터리 전압을 구독해 낮으면 경고하는 노드."""
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Float32

경고_전압 = 12.0          # V. 이보다 낮으면 충전하러 가야 한다


class 배터리감시(Node):
    def __init__(self):
        super().__init__("battery_monitor")
        self.create_subscription(Float32, "battery_voltage", self.받기, 10)

    def 받기(self, 메시지: Float32) -> None:          # 메시지가 올 때마다 불린다
        if 메시지.data < 경고_전압:
            self.get_logger().warning(f"받음: {메시지.data:.1f}V, 충전이 필요하다")
        else:
            self.get_logger().info(f"받음: {메시지.data:.1f}V")


def main() -> None:
    try:
        with rclpy.init():
            rclpy.spin(배터리감시())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == "__main__":
    main()
```

`create_subscription`은 같은 타입, 같은 토픽 이름에 콜백 `받기`를 맡깁니다. 메시지가 올 때마다 `받기`가 불리고, 전압이 12V보다 낮으면 `warning` 수준으로 로그를 남겨요. 두 노드를 함께 띄워 봅시다.

```bash
source /src/책환경.sh
뒤에서 python3 /src/배터리구독.py > /tmp/구독.txt    # 구독 노드를 뒤에서 띄워 두고
python3 /src/배터리발행.py > /tmp/발행.txt           # 발행 노드는 다섯 번 보내면 스스로 끝난다
sleep 1                                               # 마지막 메시지가 도착할 시간을 조금 준다
kill -INT %1 && wait                                  # 구독 노드에 Ctrl+C를 보낸다
echo "--- 발행 노드 ---" && cat /tmp/발행.txt
echo "--- 구독 노드 ---" && cat /tmp/구독.txt
```

```text
--- 발행 노드 ---
[INFO] [battery_publisher]: 보냄: 12.5V
[INFO] [battery_publisher]: 보냄: 12.3V
[INFO] [battery_publisher]: 보냄: 12.1V
[INFO] [battery_publisher]: 보냄: 11.9V
[INFO] [battery_publisher]: 보냄: 11.7V
--- 구독 노드 ---
[INFO] [battery_monitor]: 받음: 12.5V
[INFO] [battery_monitor]: 받음: 12.3V
[INFO] [battery_monitor]: 받음: 12.1V
[WARN] [battery_monitor]: 받음: 11.9V, 충전이 필요하다
[WARN] [battery_monitor]: 받음: 11.7V, 충전이 필요하다
```

발행 노드가 보낸 다섯 메시지를 구독 노드가 모두 받았고, 11.9V부터는 `[WARN]`으로 경고했습니다. 두 노드는 서로를 코드 어디에서도 언급하지 않고, 토픽 이름과 메시지 타입만 맞췄을 뿐이에요. 경고를 스피커로도 내고 싶으면 구독 노드를 하나 더 만들면 되고 발행 노드는 손댈 필요가 없습니다. 들어가며에서 말한 "부품 끼우기"예요.

직접 해 볼 때는 터미널 두 개에서 두 파일을 하나씩 띄우고, 구독 노드는 Ctrl+C로 멈추면 됩니다.

### 이름 규칙

변수와 함수는 한글로 지었는데 노드 이름과 토픽 이름은 영어로 적었죠. 이유가 있습니다.

```python
import rclpy
from rclpy.exceptions import InvalidNodeNameException, InvalidTopicNameException
from rclpy.node import Node
from std_msgs.msg import Float32

with rclpy.init():
    for 이름 in ["battery_monitor", "배터리감시", "battery-monitor"]:
        try:
            Node(이름).destroy_node()
            print(f"노드 이름 {이름!r}: 됨")
        except InvalidNodeNameException:
            print(f"노드 이름 {이름!r}: 안 됨")
    노드 = Node("name_test")
    for 토픽 in ["battery_voltage", "robot1/battery_voltage", "배터리", "2nd_battery"]:
        try:
            발행자 = 노드.create_publisher(Float32, 토픽, 10)
            print(f"토픽 이름 {토픽!r}: 됨 → 전체 이름 {발행자.topic_name}")
        except InvalidTopicNameException:
            print(f"토픽 이름 {토픽!r}: 안 됨")
```

```text
노드 이름 'battery_monitor': 됨
노드 이름 '배터리감시': 안 됨
노드 이름 'battery-monitor': 안 됨
토픽 이름 'battery_voltage': 됨 → 전체 이름 /battery_voltage
토픽 이름 'robot1/battery_voltage': 됨 → 전체 이름 /robot1/battery_voltage
토픽 이름 '배터리': 안 됨
토픽 이름 '2nd_battery': 안 됨
```

노드와 토픽 이름에는 **영문자, 숫자, 밑줄**만 쓸 수 있습니다. 한글과 빼기표(`-`)는 안 되고, 토픽 이름은 숫자로 시작할 수도 없어요. `robot1/battery_voltage`처럼 빗금(`/`)으로 이름을 겹겹이 나누는 것은 됩니다. 앞에 빗금 없이 적은 이름은 노드가 속한 **이름공간** 아래에 붙어서, 지금은 맨 위(`/`)에 붙어 `/battery_voltage`가 됐어요. 5.10절에서 같은 노드를 이름공간만 바꿔 로봇 두 대 몫으로 띄울 때 이 규칙이 쓸모 있습니다. 이 책은 파이썬 이름은 한글로, ROS 안에서 쓰는 이름(노드, 토픽, 서비스, 파라미터)은 영어로 짓습니다.

### 명령줄 도구로 들여다보기

노드가 여럿 돌기 시작하면 "지금 무엇이 떠 있고, 무엇이 오가는가"를 확인할 방법이 필요합니다. `ros2` 명령이 그 일을 해요. 구독 노드를 띄우고, 발행 노드 대신 `ros2 topic pub`으로 12.4V를 1초에 10번 보내면서 여러 명령을 써 보겠습니다.

```bash
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
```

```text
The daemon has been started
## 지금 떠 있는 노드
/battery_monitor
## 토픽과 타입
/battery_voltage [std_msgs/msg/Float32]
/parameter_events [rcl_interfaces/msg/ParameterEvent]
/rosout [rcl_interfaces/msg/Log]
## 토픽 하나 자세히
Type: std_msgs/msg/Float32
Publisher count: 1
Subscription count: 1
## 메시지 하나 엿보기
data: 12.399999618530273
---
## 1초에 몇 번 오나
평균 10Hz
## 구독 노드가 받은 마지막 두 메시지
[INFO] [battery_monitor]: 받음: 12.4V
[WARN] [battery_monitor]: 받음: 11.5V, 충전이 필요하다
```

- `ros2 daemon start`: 명령줄 도구가 노드 목록을 모아 두는 도우미(데몬)를 띄웁니다. 저절로도 뜨지만 막 뜬 직후에는 목록이 비어 보일 수 있어 미리 띄웠어요.
- `ros2 node list`: 떠 있는 노드 목록입니다. `ros2 topic pub`도 속으로는 `_ros2cli_37` 같은 노드를 만드는데, 밑줄로 시작하는 이름은 숨은 노드라 목록에 나오지 않아요(`--all`을 붙이면 보입니다).
- `ros2 topic list -t`: 토픽과 타입 목록입니다. 우리가 만들지 않은 `/parameter_events`와 `/rosout`은 모든 노드가 자동으로 쓰는 토픽이에요. `/rosout`에는 모든 노드의 로그가 모입니다.
- `ros2 topic info`: 토픽 하나의 타입과 발행자·구독자 수를 보여 줍니다. 메시지가 안 오면 가장 먼저 여기서 숫자를 확인하세요.
- `ros2 topic echo --once`: 오가는 메시지 하나를 엿봅니다. 12.4를 보냈는데 `12.399999618530273`이 찍혔죠? 앞에서 파이썬 안에서는 12.4였던 값이 32비트 실수로 바뀌어 보내지며 생긴 반올림이에요. 정밀도가 중요한 값은 `Float64`처럼 64비트 타입을 쓰는 이유입니다.
- `ros2 topic hz`: 메시지가 1초에 몇 번 오는지 잽니다. 원래는 `average rate: 9.994`처럼 평균과 간격의 통계를 계속 찍는데, 잴 때마다 조금씩 달라서 첫 평균만 반올림해 보였어요.
- `ros2 topic pub --once`: 명령줄에서 메시지를 한 번 보냅니다. 11.5V를 보내자 구독 노드가 경고했죠. 노드를 짜지 않고 다른 노드를 시험할 때 자주 씁니다.

## 5.4 QoS: 메시지를 어떻게 전할까

### 등기 우편과 전단지

같은 우편이라도 등기 우편은 받는 사람이 받았는지 확인하고 못 받았으면 다시 보내지만, 동네에 뿌리는 전단지는 그냥 뿌리고 끝입니다. 어느 쪽이 좋을까요? 일에 따라 다르죠. "모터를 멈춰라" 같은 명령은 반드시 도착해야 하지만, 초당 30장씩 오는 카메라 사진은 한 장쯤 빠져도 다음 장이 곧 오니, 놓친 사진을 다시 보내느라 늦어지는 것이 오히려 해롭습니다.

ROS 2는 토픽마다 이런 전달 방식을 고를 수 있게 했고, 이것을 **QoS(Quality of Service, 서비스 품질)** 라고 부릅니다. 첫 번째 정책이 **신뢰성(reliability)** 이에요. `RELIABLE`은 등기 우편, `BEST_EFFORT`는 전단지입니다. 발행자와 구독자가 각자 원하는 정책을 고르는데, 둘이 다르면 어떻게 될까요? 네 가지 조합을 모두 해 보겠습니다.

```python
import rclpy
from rclpy.event_handler import SubscriptionEventCallbacks
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, qos_profile_sensor_data
from std_msgs.msg import Int32

믿음 = ReliabilityPolicy.RELIABLE         # 등기 우편: 받았는지 확인하고, 못 받았으면 다시 보낸다
최선 = ReliabilityPolicy.BEST_EFFORT      # 전단지: 보내기만 하고 확인하지 않는다


def 실험(노드: Node, 발행_쪽: ReliabilityPolicy, 구독_쪽: ReliabilityPolicy, 토픽: str) -> None:
    받은 = []
    사건 = SubscriptionEventCallbacks(        # QoS가 맞지 않을 때 불리는 콜백
        incompatible_qos=lambda 정보: 받은.append(
            "맞지 않는 정책: " + 정보.last_policy_kind.name.removeprefix("RMW_QOS_POLICY_")))
    발행자 = 노드.create_publisher(Int32, 토픽, QoSProfile(depth=10, reliability=발행_쪽))
    노드.create_subscription(Int32, 토픽, lambda m: 받은.append(m.data),
                         QoSProfile(depth=10, reliability=구독_쪽), event_callbacks=사건)
    for _ in range(20):                       # 서로 찾을 시간(약 1초)
        rclpy.spin_once(노드, timeout_sec=0.05)
    for i in range(5):
        발행자.publish(Int32(data=i))
    for _ in range(20):                       # 메시지가 도착할 시간
        rclpy.spin_once(노드, timeout_sec=0.05)
    print(f"발행 {발행_쪽.name:11s} → 구독 {구독_쪽.name:11s}: 연결 {발행자.get_subscription_count()}개, 받은 것 {받은}")


with rclpy.init():
    노드 = Node("qos_test")
    for 번호, (발행_쪽, 구독_쪽) in enumerate([(믿음, 믿음), (최선, 최선), (믿음, 최선), (최선, 믿음)]):
        실험(노드, 발행_쪽, 구독_쪽, f"qos_demo_{번호}")

# 자주 쓰는 두 가지: 숫자 10만 적었을 때와 센서용으로 미리 정해 둔 프로파일
for 이름, 프로파일 in [("숫자 10", QoSProfile(depth=10)), ("qos_profile_sensor_data", qos_profile_sensor_data)]:
    print(f"{이름}: {프로파일.reliability.name}, {프로파일.history.name} {프로파일.depth}, {프로파일.durability.name}")
```

```text
발행 RELIABLE    → 구독 RELIABLE   : 연결 1개, 받은 것 [0, 1, 2, 3, 4]
발행 BEST_EFFORT → 구독 BEST_EFFORT: 연결 1개, 받은 것 [0, 1, 2, 3, 4]
발행 RELIABLE    → 구독 BEST_EFFORT: 연결 1개, 받은 것 [0, 1, 2, 3, 4]
발행 BEST_EFFORT → 구독 RELIABLE   : 연결 0개, 받은 것 ['맞지 않는 정책: RELIABILITY']
숫자 10: RELIABLE, KEEP_LAST 10, VOLATILE
qos_profile_sensor_data: BEST_EFFORT, KEEP_LAST 5, VOLATILE
```

세 조합은 연결되어 다섯 개를 모두 받았는데, **발행자는 전단지(`BEST_EFFORT`), 구독자는 등기(`RELIABLE`)** 인 조합만 연결이 0개입니다. 메시지가 하나도 오지 않았고, 대신 "맞지 않는 정책: RELIABILITY"라는 사건 콜백이 불렸어요. 규칙은 **발행자가 약속하는 것이 구독자가 요구하는 것 이상이어야 연결된다**입니다. 등기로 보내 주는 발행자에게 전단지면 된다는 구독자는 연결되지만, 전단지만 뿌리는 발행자에게 등기를 요구하면 연결이 안 돼요. 직접 실행하면 터미널에 `New subscription discovered on topic 'qos_demo_3', requesting incompatible QoS. No messages will be sent to it.`이라는 경고도 뜹니다.

이 함정은 실전에서 자주 만납니다. 많은 센서 드라이버가 카메라·라이다 데이터를 `BEST_EFFORT`로 보내는데, 내 구독 노드가 기본값 `RELIABLE`로 구독하면 오류도 없이 메시지가 안 오거든요. 마지막 두 줄이 그 이유를 보여 줍니다. `create_subscription(..., 10)`처럼 숫자만 적으면 `RELIABLE`이 되고, 센서용으로 미리 정해 둔 `qos_profile_sensor_data`는 `BEST_EFFORT`, 깊이 5예요. 센서 토픽을 구독할 때는 `qos_profile_sensor_data`를 쓰면 어느 쪽 발행자와도 연결됩니다.

### 기록 깊이와 지속성

QoS에는 정책이 몇 가지 더 있습니다. 많이 쓰는 두 가지를 보겠습니다. **기록 깊이(history depth)** 는 구독자가 미처 꺼내 가지 못한 메시지를 몇 개까지 쌓아 둘지이고, **지속성(durability)** 은 구독자가 **늦게 들어왔을 때** 지난 메시지를 받을 수 있는지입니다.

```python
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from std_msgs.msg import String


def 기다리기(노드: Node, 횟수: int = 20) -> None:
    for _ in range(횟수):                          # 0.05초씩 돌며 콜백을 처리한다
        rclpy.spin_once(노드, timeout_sec=0.05)


with rclpy.init():
    노드 = Node("qos_history")

    # 1) 기록 깊이: 구독자가 바빠서 못 꺼내 가는 동안 메시지 10개가 쌓이면?
    for 깊이 in [3, 10]:
        받은 = []
        발행자 = 노드.create_publisher(String, f"burst_{깊이}", QoSProfile(depth=깊이))
        노드.create_subscription(String, f"burst_{깊이}", lambda m, 받은=받은: 받은.append(m.data),
                             QoSProfile(depth=깊이))
        기다리기(노드)
        for i in range(10):                        # 콜백을 처리하지 않는 동안 10개를 몰아서 보낸다
            발행자.publish(String(data=str(i)))
        기다리기(노드)
        print(f"깊이 {깊이:2d}: 받은 것 {받은}")

    # 2) 지속성: 구독자가 늦게 들어오면 지난 메시지를 받을 수 있나?
    게시판 = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
    발행자 = 노드.create_publisher(String, "map", 게시판)
    for 판 in ["지도 1판", "지도 2판"]:            # 구독자가 아무도 없을 때 보낸다
        발행자.publish(String(data=판))
    for 이름, 지속성 in [("VOLATILE", DurabilityPolicy.VOLATILE),
                       ("TRANSIENT_LOCAL", DurabilityPolicy.TRANSIENT_LOCAL)]:
        받은 = []
        노드.create_subscription(String, "map", lambda m, 받은=받은: 받은.append(m.data),
                             QoSProfile(depth=1, durability=지속성))
        기다리기(노드)
        print(f"늦게 온 구독자({이름:15s}): 받은 것 {받은}")
```

```text
깊이  3: 받은 것 ['7', '8', '9']
깊이 10: 받은 것 ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
늦게 온 구독자(VOLATILE       ): 받은 것 []
늦게 온 구독자(TRANSIENT_LOCAL): 받은 것 ['지도 2판']
```

첫 실험에서는 구독자가 콜백을 처리하지 않는 동안 메시지 10개를 몰아서 보냈습니다. 깊이 3이면 마지막 3개(7, 8, 9)만 남고 앞의 7개는 밀려났어요. 깊이 10이면 모두 받았습니다. 우편함이 작으면 오래된 편지부터 버려지는 셈이에요. 위치나 센서 값처럼 **최신 값만 중요한** 토픽은 깊이를 작게 두는 것이 맞습니다. 늦게 처리한 옛날 위치로 판단하면 1장 1.4절의 "늦게 도착하는 측정" 문제가 생기니까요.

둘째 실험에서는 아무도 구독하지 않을 때 "지도 1판", "지도 2판"을 보낸 뒤 구독자를 붙였습니다. 기본값 `VOLATILE`(휘발성) 구독자는 아무것도 못 받았고, `TRANSIENT_LOCAL` 구독자는 마지막 판인 "지도 2판"을 받았어요. 발행자가 깊이 1만큼 최근 메시지를 들고 있다가 새로 온 구독자에게 건네준 것입니다. 동네 게시판에 붙여 둔 공지처럼, 한 번 정해지면 잘 안 바뀌지만 누구든 언제 와도 알아야 하는 정보(지도, 로봇의 모양 설명)에 씁니다. 6장에서 볼 로봇 설명 토픽도 이 방식으로 발행돼요.

| 정책 | 값 | 뜻 | 어울리는 곳 |
|---|---|---|---|
| 신뢰성 | `RELIABLE` | 확인하고 다시 보낸다 | 명령, 상태 변화 |
| | `BEST_EFFORT` | 보내기만 한다 | 카메라, 라이다처럼 빠르고 많은 센서 |
| 기록 | `KEEP_LAST` + 깊이 | 최근 N개만 쌓아 둔다 | 대부분 |
| 지속성 | `VOLATILE` | 지금부터 오는 것만 | 대부분 |
| | `TRANSIENT_LOCAL` | 늦게 온 구독자에게 최근 것을 준다 | 지도, 로봇 설명, 설정 |

## 5.5 서비스: 물어보고 답 듣기

### 토픽, 서비스, 액션

토픽은 방송이라 보내는 쪽이 답을 받지 않습니다. 그런데 "모터를 켜 줘"라고 했을 때는 정말 켜졌는지 답을 들어야 하죠. 이렇게 **요청을 보내고 응답을 받는** 통신이 **서비스(service)** 입니다. 전화로 물어보고 대답을 듣는 것과 같아요. 그리고 "저기까지 가 줘"처럼 오래 걸리는 일에는 중간에 "지금 반쯤 왔어요"라는 소식을 듣고 싶고, 마음이 바뀌면 취소도 하고 싶습니다. 이런 일을 위한 것이 **액션(action)** 이에요. 세 가지를 정리하면 이렇습니다.

| 통신 | 모양 | 비유 | 예 | 언제 |
|---|---|---|---|---|
| 토픽 | 한쪽으로 계속 흘려보낸다 | 방송 | 센서 값, 속도 명령, 위치 | 계속 바뀌는 값 |
| 서비스 | 요청 한 번, 응답 한 번 | 전화 문의 | 모터 켜기, 설정 바꾸기, 지도 받기 | 금방 끝나는 일 |
| 액션 | 목표 → 중간 피드백 → 결과, 취소 가능 | 택배 배송 조회 | 목표까지 이동, 물건 잡기 | 몇 초 이상 걸리는 일 |

서비스는 응답이 올 때까지 부르는 쪽이 기다리니, 몇 초씩 걸리는 일을 서비스로 만들면 그동안 아무 소식도 없이 기다려야 합니다. 그래서 금방 끝나는 일은 서비스, 오래 걸리는 일은 액션으로 나눠요. 액션은 5.9절에서 만들고, 여기서는 서비스를 만들어 봅니다.

### 서비스 서버와 클라이언트

모터를 켜고 끄는 서비스를 만들겠습니다. 요청은 참/거짓 하나, 응답은 성공 여부와 설명인 `std_srvs/srv/SetBool` 타입을 써요. 서비스를 제공하는 쪽이 **서버**입니다.

```python
"""5.5절: 모터를 켜고 끄는 서비스를 제공하는 노드."""
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_srvs.srv import SetBool


class 모터드라이버(Node):
    def __init__(self):
        super().__init__("motor_driver")
        self.켜짐 = False
        self.create_service(SetBool, "enable_motor", self.요청_처리)   # 타입, 서비스 이름, 콜백

    def 요청_처리(self, 요청: SetBool.Request, 응답: SetBool.Response) -> SetBool.Response:
        if 요청.data == self.켜짐:                     # 이미 그 상태면 거절한다
            응답.success = False
            응답.message = "이미 켜져 있다" if self.켜짐 else "이미 꺼져 있다"
        else:
            self.켜짐 = 요청.data
            응답.success = True
            응답.message = "모터를 켰다" if self.켜짐 else "모터를 껐다"
        self.get_logger().info(f"요청 {요청.data} → {응답.message}")
        return 응답


def main() -> None:
    try:
        with rclpy.init():
            rclpy.spin(모터드라이버())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == "__main__":
    main()
```

`create_service`에 타입, 서비스 이름, 콜백을 줍니다. 콜백은 요청을 받아 응답을 채워 돌려줘요. 이미 켜진 모터를 또 켜라고 하면 거절하게 했습니다. 서비스를 부르는 쪽은 **클라이언트**예요.

```python
"""5.5절: 모터 서비스를 부르는 클라이언트. 켜기, 다시 켜기, 끄기를 차례로 요청한다."""
import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool

with rclpy.init():
    노드 = Node("motor_switch")
    클라이언트 = 노드.create_client(SetBool, "enable_motor")
    if not 클라이언트.wait_for_service(timeout_sec=5.0):          # 서버가 뜰 때까지 기다린다
        raise RuntimeError("enable_motor 서비스가 없다")
    for 켜기 in [True, True, False]:
        미래 = 클라이언트.call_async(SetBool.Request(data=켜기))   # 요청을 보내고 바로 돌아온다
        rclpy.spin_until_future_complete(노드, 미래, timeout_sec=5.0)   # 응답이 올 때까지 돌며 기다린다
        응답 = 미래.result()
        print(f"켜기={켜기!s:5s} → 성공 {응답.success}, '{응답.message}'")
```

`wait_for_service`로 서버가 뜰 때까지 기다린 뒤, `call_async`로 요청을 보냅니다. `call_async`는 응답을 기다리지 않고 바로 **미래(future)** 라는 "나중에 답이 담길 상자"를 돌려줘요. `spin_until_future_complete`가 그 상자에 답이 담길 때까지 노드를 돌립니다. 서버를 띄우고 파이썬 클라이언트와 명령줄로 불러 보겠습니다.

```bash
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
```

```text
켜기=True  → 성공 True, '모터를 켰다'
켜기=True  → 성공 False, '이미 켜져 있다'
켜기=False → 성공 True, '모터를 껐다'
## 명령줄에서
/enable_motor
/motor_driver/describe_parameters
/motor_driver/get_parameter_types
/motor_driver/get_parameters
/motor_driver/get_type_description
/motor_driver/list_parameters
/motor_driver/set_parameters
/motor_driver/set_parameters_atomically
std_srvs/srv/SetBool
bool data # e.g. for hardware enabling / disabling
---
bool success   # indicate successful run of triggered service
string message # informational, e.g. for error messages
std_srvs.srv.SetBool_Response(success=True, message='모터를 켰다')

## 서버의 로그
[INFO] [motor_driver]: 요청 True → 모터를 켰다
[INFO] [motor_driver]: 요청 True → 이미 켜져 있다
[INFO] [motor_driver]: 요청 False → 모터를 껐다
[INFO] [motor_driver]: 요청 True → 모터를 켰다
```

켜기는 성공, 다시 켜기는 "이미 켜져 있다"로 거절, 끄기는 성공입니다. 명령줄의 `ros2 service call`로도 똑같이 부를 수 있어요. 응답이 꺼진 모터를 켰다고 알려 줬죠.

`ros2 service list`의 결과에 우리가 만들지 않은 서비스가 7개나 더 있는 것이 눈에 띕니다. 이름에 노드 이름이 붙은 이 서비스들은 모든 노드가 자동으로 가지는 것이에요. `get_type_description`(메시지 타입의 설명을 알려 준다)을 뺀 6개가 **파라미터 서비스**로, 다음 절의 파라미터가 사실은 이 서비스들로 오갑니다.

> **Q. `call_async` 대신 응답을 기다리는 `call`을 쓰면 더 간단하지 않나요?**
> `call`도 있습니다. 응답이 올 때까지 그 자리에서 멈춰 기다리는 함수예요. 문제는 콜백 안에서 부를 때입니다. 응답이 도착했다는 것을 알아채는 일도 같은 `spin`이 해야 하는데, `spin`은 지금 그 콜백이 끝나기를 기다리고 있죠. 서로가 서로를 기다리니 영영 끝나지 않습니다. 실제로 타이머 콜백 안에서 `call`을 `timeout_sec=3.0`과 함께 불러 보면, 서버가 멀쩡히 떠 있는데도 3초 뒤 `TimeoutError`가 납니다. 콜백 안에서는 `call_async`를 쓰고, 응답은 미래에 콜백을 달아 받으세요.

## 5.6 파라미터: 노드의 설정 손잡이

### 코드를 고치지 않고 값 바꾸기

1장의 점 로봇에는 이득 1.5, 최대 속도 0.5m/s 같은 숫자가 코드에 박혀 있었습니다. 숫자 하나 바꾸려고 코드를 고치면 번거롭고 실수하기도 쉽죠. ROS 2 노드는 이런 값을 **파라미터(parameter)** 로 꺼내 둘 수 있습니다. 노드를 띄울 때 바꿀 수도 있고, 도는 중에 바꿀 수도 있어요. 라디오의 음량 손잡이처럼 겉으로 꺼내 둔 설정이라고 생각하면 됩니다.

최대 속도를 파라미터로 받는 노드를 만들어 보겠습니다. 1장 1.7절에서 본 것처럼 속도 제한은 안전과 직결되니, 엉뚱한 값은 거절하게 할게요.

```python
"""5.6절: 최대 속도를 파라미터로 받는 노드. 바꿀 때마다 값을 검사한다."""
import rclpy
from rcl_interfaces.msg import SetParametersResult
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.parameter import Parameter

안전_한계 = 1.0     # m/s. 누가 뭐라 해도 이보다 빠르게는 못 바꾼다


class 속도제한(Node):
    def __init__(self):
        super().__init__("speed_limiter")
        self.add_on_set_parameters_callback(self.바꾸기_전_검사)   # 검사부터 걸어 두고
        self.declare_parameter("max_speed", 0.5)        # 선언한다: 이름과 기본값(타입은 기본값으로 정해진다)
        self.declare_parameter("robot_name", "pointbot")
        최대 = self.get_parameter("max_speed").value
        이름 = self.get_parameter("robot_name").value
        self.get_logger().info(f"{이름}의 최대 속도 {최대}m/s로 시작")

    def 바꾸기_전_검사(self, 바뀔_것들: list[Parameter]) -> SetParametersResult:
        for p in 바뀔_것들:
            if p.name == "max_speed" and not 0.0 < p.value <= 안전_한계:
                return SetParametersResult(successful=False, reason=f"0보다 크고 {안전_한계} 이하여야 한다")
            self.get_logger().info(f"{p.name} = {p.value}")
        return SetParametersResult(successful=True)


def main() -> None:
    try:
        with rclpy.init():
            rclpy.spin(속도제한())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == "__main__":
    main()
```

`declare_parameter`로 파라미터의 이름과 기본값을 선언합니다. 타입은 기본값에서 정해져서, `0.5`를 주었으니 `max_speed`는 실수 파라미터예요. `add_on_set_parameters_callback`은 파라미터가 바뀌기 **직전에** 불릴 검사 함수를 겁니다. 검사 함수가 `successful=False`를 돌려주면 바뀌지 않아요. 명령줄에서 여러 가지로 다뤄 보겠습니다.

```bash
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
```

```text
## 파라미터 목록
  max_speed
  robot_name
  start_type_description_service
  use_sim_time
## 읽기
Double value is: 0.3
## 바꾸기
Set parameter successful
## 너무 큰 값
Setting parameter failed: 0보다 크고 1.0 이하여야 한다
## 타입이 다른 값
Setting parameter failed: Wrong parameter type, expected '3' got '4'
## 지금 값을 파일로
/speed_limiter:
  ros__parameters:
    max_speed: 0.8
    robot_name: pointbot
    start_type_description_service: true
    use_sim_time: false

## 노드의 로그
[INFO] [speed_limiter]: max_speed = 0.3
[INFO] [speed_limiter]: robot_name = pointbot
[INFO] [speed_limiter]: pointbot의 최대 속도 0.3m/s로 시작
[INFO] [speed_limiter]: max_speed = 0.8
## 시작할 때부터 너무 큰 값
rclpy.exceptions.InvalidParameterValueException: Invalid parameter value (2.0) for parameter. Reason: 0보다 크고 1.0 이하여야 한다: max_speed
```

- `--ros-args -p max_speed:=0.3`: 노드를 띄우면서 파라미터를 줍니다. 노드의 로그에서 0.3으로 시작한 것을 볼 수 있어요.
- `ros2 param list`: 우리가 선언한 두 개 말고도 `use_sim_time`(5.7절)과 `start_type_description_service`가 있습니다. 모든 노드가 기본으로 가지는 파라미터예요.
- `ros2 param set ... 0.8`: 도는 중에 바꿨고, 검사를 통과해 노드의 로그에도 `max_speed = 0.8`이 찍혔습니다.
- `5.0`은 검사 함수가 거절했고, 그 이유가 그대로 전해졌어요. 문자 `fast`는 검사 함수에 닿기도 전에 타입 검사에서 걸렸습니다. 메시지의 `expected '3' got '4'`는 실수(3)를 기대했는데 문자열(4)이 왔다는 뜻이에요.
- `ros2 param dump`: 지금 값을 YAML 파일 모양으로 꺼냅니다. 이 파일을 저장해 두었다가 `--ros-args --params-file 설정.yaml`로 노드를 띄우면 같은 설정으로 시작해요.

마지막 줄도 중요합니다. 시작할 때부터 2.0을 주자 노드가 아예 뜨지 않고 `InvalidParameterValueException`으로 끝났어요. 검사 함수를 `declare_parameter`보다 **먼저** 걸어 두었기 때문입니다. 순서를 바꿔 선언을 먼저 하고 검사를 나중에 걸면, 시작할 때 준 값은 검사를 거치지 않아 2.0m/s로 그대로 시작해 버립니다. 실제로 그렇게 바꿔 실행해 보면 `pointbot의 최대 속도 2.0m/s로 시작`이 찍혀요. 안전에 관계된 값이라면 검사부터 걸고 선언하세요.

## 5.7 시간: 실행기, 타이머, 시각

### 실행기: 콜백을 부르는 일꾼

5.2절에서 `spin`이 콜백을 불러 준다고 했습니다. 이 일을 실제로 하는 것은 **실행기(executor)** 예요. `rclpy.spin(노드)`는 기본 실행기인 `SingleThreadedExecutor`를 만들어 씁니다. 이름처럼 일꾼 한 명이 콜백을 **하나씩 차례로** 부르죠. 그러면 들어가며의 문제가 노드 안에서 다시 생기지 않을까요? 0.01초마다 도는 모터 타이머와, 한 번에 0.2초 걸리는 카메라 처리 타이머를 한 노드에 넣어 보겠습니다.

```python
import time

import rclpy
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor, SingleThreadedExecutor
from rclpy.node import Node


class 한몸로봇(Node):
    """모터 고리(0.01초마다)와 느린 카메라 처리(0.5초마다, 한 번에 0.2초)를 한 노드에 넣었다."""

    def __init__(self, 무리_나누기: bool):
        super().__init__("one_body_robot")
        모터_무리 = MutuallyExclusiveCallbackGroup() if 무리_나누기 else None
        카메라_무리 = MutuallyExclusiveCallbackGroup() if 무리_나누기 else None
        self.모터_시각들 = []
        self.create_timer(0.01, self.모터, callback_group=모터_무리)
        self.create_timer(0.5, self.카메라, callback_group=카메라_무리)

    def 모터(self) -> None:
        self.모터_시각들.append(time.monotonic())

    def 카메라(self) -> None:
        time.sleep(0.2)                     # 사진에서 물체를 찾느라 0.2초 걸린다


def 재기(실행기, 무리_나누기: bool) -> None:
    노드 = 한몸로봇(무리_나누기)
    실행기.add_node(노드)
    끝 = time.monotonic() + 2.0
    while time.monotonic() < 끝:            # 2초 동안 돌린다
        실행기.spin_once(timeout_sec=0.01)
    실행기.remove_node(노드)
    간격들 = [b - a for a, b in zip(노드.모터_시각들, 노드.모터_시각들[1:])]
    print(f"{type(실행기).__name__:22s}: 모터 고리의 가장 긴 간격 {max(간격들):.1f}초")
    노드.destroy_node()


with rclpy.init():
    재기(SingleThreadedExecutor(), 무리_나누기=False)
    재기(MultiThreadedExecutor(num_threads=2), 무리_나누기=True)
```

```text
SingleThreadedExecutor: 모터 고리의 가장 긴 간격 0.2초
MultiThreadedExecutor : 모터 고리의 가장 긴 간격 0.0초
```

일꾼이 한 명인 `SingleThreadedExecutor`에서는 모터 고리가 0.2초나 멈춘 적이 있습니다. 카메라 콜백이 도는 동안 모터 콜백 차례가 오지 않았기 때문이에요. 노드로 나눴어도 **한 노드 안에 무거운 콜백과 급한 콜백을 섞으면** 들어가며와 같은 문제가 그대로 생깁니다. 일꾼을 둘 둔 `MultiThreadedExecutor`에서 두 타이머를 서로 다른 **콜백 그룹**에 넣자, 모터 고리의 가장 긴 간격이 0.05초도 안 되는 0.0초가 됐어요. 카메라 콜백이 도는 동안 다른 일꾼이 모터 콜백을 불렀기 때문입니다.

콜백 그룹은 "이 콜백들은 동시에 돌면 안 된다"는 묶음입니다. 같은 `MutuallyExclusiveCallbackGroup`에 든 콜백은 하나씩만 돌고, 다른 그룹의 콜백끼리는 동시에 돌 수 있어요. 그룹을 주지 않으면 노드의 모든 콜백이 한 그룹이라 일꾼이 여럿이어도 하나씩만 돕니다. 더 단순한 방법은 들어가며의 결론대로 무거운 일을 **아예 다른 노드, 다른 프로세스**로 떼어 내는 것이에요. 다중 스레드 실행기는 한 노드 안에서 꼭 동시에 돌아야 할 콜백이 있을 때 씁니다.

1장 1.4절의 "할 일이 주기보다 오래 걸리면 박자를 놓친다"는 ROS 2의 타이머에도 그대로 해당합니다. 빠른 고리를 맡은 콜백은 짧게 유지하세요.

### 메시지의 시각

메시지가 늦게 도착할 수 있다는 것도 1장 1.4절에서 봤습니다. 늦게 온 측정을 제대로 다루려면 먼저 **언제 잰 값인지**를 알아야 하죠. 그래서 `Stamped` 메시지의 머리말에 시각을 적어 보냅니다.

```python
from geometry_msgs.msg import PointStamped
from rclpy.clock import ClockType
from rclpy.time import Time

# 카메라가 시각 12.4초에 찍은 사진에서 컵을 찾았다. 처리에 시간이 걸려 12.7초에 판단 노드에 도착했다
메시지 = PointStamped()
메시지.header.stamp = Time(seconds=12, nanoseconds=400_000_000).to_msg()   # 언제 잰 값인가
메시지.header.frame_id = "camera"                                          # 어느 좌표계로 잰 값인가
메시지.point.x, 메시지.point.y, 메시지.point.z = 0.1, -0.05, 0.8
print(메시지.header)

# 노드 안이라면 self.get_clock().now()로 받는 '지금'. 그 시계와 같은 종류(ROS_TIME)로 만든다
지금 = Time(seconds=12, nanoseconds=700_000_000, clock_type=ClockType.ROS_TIME)
늦음 = 지금 - Time.from_msg(메시지.header.stamp)           # 시각 - 시각 = 시간 간격(Duration)
print(f"이 측정은 {늦음.nanoseconds / 1e9:.1f}초 전의 세상이다")
```

```text
std_msgs.msg.Header(stamp=builtin_interfaces.msg.Time(sec=12, nanosec=400000000), frame_id='camera')
이 측정은 0.3초 전의 세상이다
```

머리말의 `stamp`는 초(`sec`)와 나노초(`nanosec`) 두 칸으로 되어 있습니다. 받은 쪽은 지금 시각에서 `stamp`를 빼서 "이 측정이 0.3초 전의 세상"이라는 것을 알 수 있어요. 1장에서는 로봇이 측정이 얼마나 늦었는지 몰라서 지나치고 흔들렸지만, 시각을 알면 그동안 움직인 만큼을 고려해 판단할 수 있습니다. 노드 안에서는 지금 시각을 `self.get_clock().now()`로 얻어요. 이 시계와 같은 종류(`ROS_TIME`)의 시각끼리만 뺄 수 있어서, 블록에서는 `clock_type`을 맞춰 만들었습니다. 종류가 다른 시각을 빼면 `Can't subtract times with different clock types`라는 오류가 나요.

`frame_id`의 `"camera"`는 이 값이 카메라 좌표계로 잰 값이라는 표시입니다. 2장에서 손으로 하던 "카메라 기준 값을 방 기준으로 바꾸기"를 ROS 2에서는 이 이름표를 보고 tf2라는 도구가 해 주는데, 6장에서 만납니다.

### 시뮬레이션 시간

4장의 MuJoCo는 진짜 시간과 상관없이 `mj_step` 한 번에 정해진 시간 간격만큼 시뮬레이션을 진행했죠. 계산이 빠르면 진짜 1초 동안 시뮬레이션 10초가 흐를 수도 있고, 느리면 반대일 수도 있습니다. 그렇다면 노드의 타이머는 어느 시간을 따라야 할까요? ROS 2에는 이를 위한 약속이 있습니다. 시뮬레이터가 `/clock` 토픽으로 "지금 시뮬레이션 시각"을 발행하고, 노드는 파라미터 `use_sim_time`을 켜면 벽시계 대신 이 시각을 따라요.

```python
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rosgraph_msgs.msg import Clock
from rclpy.time import Time

with rclpy.init():
    # 시뮬레이터 흉내: /clock 토픽으로 '지금 시뮬레이션 시각'을 알린다
    시계_노드 = Node("fake_simulator")
    시계_발행자 = 시계_노드.create_publisher(Clock, "/clock", 10)

    # use_sim_time을 켠 노드: 벽시계 대신 /clock을 시계로 쓴다
    제어_노드 = Node("controller", parameter_overrides=[Parameter("use_sim_time", value=True)])
    제어_노드.create_timer(1.0, lambda: print(f"타이머: 시뮬레이션 시각 {제어_노드.get_clock().now().nanoseconds / 1e9:.1f}초"))

    실행기 = rclpy.executors.SingleThreadedExecutor()
    실행기.add_node(시계_노드)
    실행기.add_node(제어_노드)
    for _ in range(20):
        실행기.spin_once(timeout_sec=0.05)
    for 걸음 in range(1, 36):               # 시뮬레이션 시간을 0.1초씩 3.5초까지 흘린다
        시계_발행자.publish(Clock(clock=Time(nanoseconds=걸음 * 100_000_000).to_msg()))
        for _ in range(3):
            실행기.spin_once(timeout_sec=0.01)
    print("제어 노드의 시각:", 제어_노드.get_clock().now().nanoseconds / 1e9, "초")
    print("시계 노드의 시각:", 시계_노드.get_clock().now().nanoseconds / 1e9 > 1e9, "(벽시계: 1970년부터 센 초)")
```

```text
타이머: 시뮬레이션 시각 1.0초
타이머: 시뮬레이션 시각 2.0초
타이머: 시뮬레이션 시각 3.0초
제어 노드의 시각: 3.5 초
시계 노드의 시각: True (벽시계: 1970년부터 센 초)
```

`/clock`에 0.1초씩 늘어나는 시각을 35번 보냈더니, 1초짜리 타이머가 시뮬레이션 시각 1.0, 2.0, 3.0초에 정확히 불렸습니다. 진짜로 흐른 시간과는 상관없어요. 제어 노드의 시계는 3.5초를 가리키는데, `use_sim_time`을 켜지 않은 시계 노드는 1970년부터 센 진짜 시각을 그대로 씁니다. 이렇게 해 두면 시뮬레이터를 빠르게 돌리든 느리게 돌리든 제어 노드는 늘 같은 박자로 판단하고, 진짜 로봇으로 옮길 때는 `use_sim_time`만 끄면 됩니다.

## 5.8 패키지: 노드를 묶어 나눠 주기

### 왜 패키지로 묶을까

지금까지는 파일을 직접 실행했습니다. 노드가 늘어나고 다른 사람과 나누려면 "이 노드들이 어디 있고, 무엇에 기대고, 어떻게 실행하는가"를 정해 둔 묶음이 필요해요. 그 묶음이 **패키지(package)** 입니다. 1권 14장에서 파이썬 모듈을 패키지로 묶었던 것과 같은 생각인데, ROS 2 패키지에는 의존하는 ROS 패키지 목록과 실행 파일 이름이 더 들어갑니다.

파이썬 노드를 담는 패키지는 **ament_python** 방식으로 만듭니다. 여러 패키지를 모아 두는 폴더를 **작업 공간(workspace)** 이라 하고, 작업 공간을 빌드하는 도구가 **colcon**이에요. 이 장에서는 패키지를 두 번 만드니, 과정을 함수 하나로 묶어 두겠습니다.

```bash
# 5.8절: /tmp/ws 작업 공간에 ament_python 패키지를 만들고 노드 파일을 넣어 빌드하는 함수
# 사용: 패키지_만들기 <패키지 이름> <실행 이름>=<노드 파일> ...
# (bash 변수 이름에는 한글을 쓸 수 없어서 영어로 적었다)
패키지_만들기() {
    local pkg=$1; shift
    local entries="" here=$PWD                       # 끝나면 돌아올 폴더
    mkdir -p /tmp/ws/src && cd /tmp/ws/src
    ros2 pkg create "$pkg" --build-type ament_python --license MIT \
        --dependencies rclpy std_msgs geometry_msgs > /dev/null
    for item in "$@"; do
        local exe=${item%%=*} file=${item#*=}        # "battery_publisher=배터리발행.py"를 둘로 나눈다
        cp "/src/$file" "$pkg/$pkg/"                 # 파일을 패키지의 파이썬 폴더에 넣는다
        if [[ $item == *=* ]]; then                  # 실행 이름이 붙은 파일은 노드로 등록한다
            entries+="            '$exe = $pkg.${file%.py}:main',"$'\n'
        fi
    done
    cat > "$pkg/setup.py" <<SETUP
from setuptools import find_packages, setup

setup(
    name='$pkg',
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/$pkg']),
        ('share/$pkg', ['package.xml']),
    ],
    install_requires=['setuptools'],
    entry_points={
        'console_scripts': [
$entries        ],
    },
)
SETUP
    cd /tmp/ws && colcon build --packages-select "$pkg" > /tmp/빌드.txt   # 빌드 기록은 파일로 남긴다
    source /tmp/ws/install/setup.bash                 # 새로 지은 패키지를 이 셸에서 쓸 수 있게 한다
    cd "$here"
}
```

순서는 이렇습니다.

1. `ros2 pkg create`로 패키지의 뼈대를 만듭니다. `--build-type ament_python`은 파이썬 패키지, `--dependencies`는 이 패키지가 기대는 ROS 패키지들이에요.
2. 노드 파일을 패키지 이름과 같은 안쪽 폴더에 복사합니다.
3. `setup.py`를 씁니다. 핵심은 `entry_points`의 `console_scripts`예요. `'battery_publisher = battery_demo.배터리발행:main'`은 "`battery_publisher`라는 실행 파일을 부르면 `battery_demo` 패키지의 `배터리발행` 모듈에 있는 `main` 함수를 실행하라"는 뜻입니다. 노드 파일마다 `main` 함수를 둔 이유가 이것이에요.
4. 작업 공간 맨 위에서 `colcon build`로 빌드하고, `install/setup.bash`를 불러와 새 패키지를 이 셸에 알립니다. 새 터미널을 열 때마다 이 `source`를 다시 해야 해요.

배터리 노드 두 개를 `battery_demo` 패키지로 묶고 실행해 보겠습니다.

```bash
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
```

```text
## 패키지 폴더
battery_demo/LICENSE
battery_demo/battery_demo/__init__.py
battery_demo/battery_demo/py.typed
battery_demo/battery_demo/배터리구독.py
battery_demo/battery_demo/배터리발행.py
battery_demo/package.xml
battery_demo/resource/battery_demo
battery_demo/setup.cfg
battery_demo/setup.py
## 진입점(setup.py의 일부)
        'console_scripts': [
            'battery_publisher = battery_demo.배터리발행:main',
            'battery_monitor = battery_demo.배터리구독:main',
        ],
## 의존 패키지(package.xml의 일부)
  <depend>rclpy</depend>
  <depend>std_msgs</depend>
  <depend>geometry_msgs</depend>
## 빌드 기록(걸린 시간은 지웠다)
Starting >>> battery_demo
Finished <<< battery_demo

Summary: 1 package finished
## 작업 공간
build
install
log
src
## 이 패키지의 실행 파일
battery_demo battery_monitor
battery_demo battery_publisher
## ros2 run으로 실행
[INFO] [battery_monitor]: 받음: 12.5V
[INFO] [battery_monitor]: 받음: 12.3V
[INFO] [battery_monitor]: 받음: 12.1V
[WARN] [battery_monitor]: 받음: 11.9V, 충전이 필요하다
[WARN] [battery_monitor]: 받음: 11.7V, 충전이 필요하다
[ros2run]: Received signal:  Interrupt
```

`ros2 pkg create`가 만든 파일 가운데 눈여겨볼 것은 세 가지입니다. `package.xml`은 패키지의 이름, 판, 라이선스, 의존 패키지(`<depend>`)를 적은 명함이고, `setup.py`는 파이썬 쪽 설치 방법이며, `resource/battery_demo`는 "여기 이런 패키지가 있다"고 ROS에 알리는 빈 표시 파일이에요. 빌드하면 작업 공간에 `build`(빌드 중간물), `install`(설치된 결과), `log`(빌드 기록) 폴더가 생깁니다. 패키지를 고쳤으면 다시 빌드해야 `install`에 반영되니 주의하세요.

이제 `ros2 run 패키지 실행이름`으로 어느 폴더에서든 노드를 띄울 수 있습니다. 마지막 줄의 `[ros2run]: Received signal: Interrupt`는 `ros2 run`이 Ctrl+C를 받아 노드에 전했다는 알림이에요.

## 5.9 액션: 오래 걸리는 일 맡기기

### 액션 타입 만들기

액션은 세 부분으로 이루어집니다. 무엇을 할지(**목표**), 하는 동안의 소식(**피드백**), 끝났을 때의 **결과**예요. 택배 주문(목표)을 넣으면 "출발했어요, 동네에 왔어요"(피드백)를 받다가 "도착했어요"(결과)를 받고, 그사이에 취소할 수도 있는 것과 같습니다.

점 로봇을 목표까지 보내는 액션에 알맞은 타입은 설치되어 있지 않으니 직접 만듭니다. 메시지·서비스·액션 타입은 C++와 파이썬 코드를 함께 만들어 내야 해서, 파이썬 패키지가 아니라 **ament_cmake** 방식의 **인터페이스 패키지**로 만듭니다.

```bash
# 5.9절: 액션 타입 MoveTo를 담은 인터페이스 패키지를 만들어 빌드한다
mkdir -p /tmp/ws/src/robot_interfaces/action && cd /tmp/ws/src/robot_interfaces

cat > action/MoveTo.action <<'DEF'
# 목표: 어디로 갈까
float64 x
float64 y
---
# 결과: 끝났을 때 목표까지 남은 거리(m)
float64 error
---
# 중간 피드백: 지금 남은 거리(m)
float64 remaining
DEF

cat > CMakeLists.txt <<'DEF'
cmake_minimum_required(VERSION 3.20)
project(robot_interfaces)
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
rosidl_generate_interfaces(${PROJECT_NAME} "action/MoveTo.action")
ament_package()
DEF

cat > package.xml <<'DEF'
<?xml version="1.0"?>
<package format="3">
  <name>robot_interfaces</name>
  <version>0.1.0</version>
  <description>점 로봇의 액션 타입</description>
  <maintainer email="reader@example.com">reader</maintainer>
  <license>MIT</license>
  <buildtool_depend>ament_cmake</buildtool_depend>
  <buildtool_depend>rosidl_default_generators</buildtool_depend>
  <exec_depend>rosidl_default_runtime</exec_depend>
  <member_of_group>rosidl_interface_packages</member_of_group>
  <export><build_type>ament_cmake</build_type></export>
</package>
DEF

cd /tmp/ws && colcon build --packages-select robot_interfaces > /tmp/빌드.txt
source /tmp/ws/install/setup.bash
```

`MoveTo.action` 파일이 액션 타입의 정의입니다. `---` 두 줄로 목표, 결과, 피드백을 나눠요. 순서가 목표 → 결과 → 피드백이라는 점에 주의하세요. `CMakeLists.txt`의 `rosidl_generate_interfaces`가 이 정의에서 파이썬과 C++ 코드를 만들어 내고, `package.xml`의 `member_of_group`은 이 패키지가 인터페이스 패키지라고 알립니다. 빌드가 끝나면 파이썬에서 `from robot_interfaces.action import MoveTo`로 쓸 수 있어요.

### 액션 서버와 클라이언트

액션 서버는 1장의 점 로봇을 그대로 씁니다. 1장의 `점로봇.py`를 이 장 폴더에 복사해 `움직이기`를 가져왔어요. 이득 1.5의 비례 제어로 목표까지 가면서 1초마다 남은 거리를 피드백으로 보내고, 5m보다 먼 목표는 아예 받지 않습니다. 기다리는 시간을 줄이려고 시간은 10배 빠르게 흘려요.

```python
"""5.9절: 1장의 점 로봇을 목표까지 움직이는 액션 서버. 시간은 10배 빠르게 흘린다."""
import time

import numpy as np
import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node
from robot_interfaces.action import MoveTo

from 점로봇 import 움직이기

주기, 이득 = 0.1, 1.5
최대_거리 = 5.0          # m. 이보다 먼 목표는 받지 않는다


class 이동서버(Node):
    def __init__(self):
        super().__init__("move_server")
        self.위치 = np.array([0.0, 0.0])
        ActionServer(self, MoveTo, "move_to", execute_callback=self.실행,
                     goal_callback=self.목표_검사, cancel_callback=lambda 요청: CancelResponse.ACCEPT)

    def 목표_검사(self, 목표: MoveTo.Goal) -> GoalResponse:
        거리 = np.linalg.norm(np.array([목표.x, 목표.y]) - self.위치)
        return GoalResponse.ACCEPT if 거리 <= 최대_거리 else GoalResponse.REJECT

    def 실행(self, 목표_핸들) -> MoveTo.Result:
        목표 = np.array([목표_핸들.request.x, 목표_핸들.request.y])
        for 걸음 in range(1, 101):                       # 최대 10초(100걸음)
            if 목표_핸들.is_cancel_requested:             # 취소 요청이 왔으면 그 자리에 선다
                목표_핸들.canceled()
                return MoveTo.Result(error=float(np.linalg.norm(목표 - self.위치)))
            self.위치 = 움직이기(self.위치, 이득 * (목표 - self.위치), 주기)
            남은 = float(np.linalg.norm(목표 - self.위치))
            if 걸음 % 10 == 0:                             # 1초마다 중간 소식을 보낸다
                목표_핸들.publish_feedback(MoveTo.Feedback(remaining=남은))
            if 남은 < 0.01:
                break
            time.sleep(주기 / 10)                         # 진짜 시간보다 10배 빠르게
        목표_핸들.succeed()
        return MoveTo.Result(error=남은)


def main() -> None:
    try:
        with rclpy.init():
            rclpy.spin(이동서버(), executor=MultiThreadedExecutor())   # 실행 중에도 취소를 받으려면 여러 스레드로
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == "__main__":
    main()
```

`ActionServer`에 콜백 세 개를 맡깁니다. `goal_callback`은 목표를 받을지 정하고, `execute_callback`은 실제 일을 하고, `cancel_callback`은 취소 요청을 받을지 정해요. 실행 콜백 `실행` 안에서는 걸음마다 `is_cancel_requested`로 취소 요청이 왔는지 확인합니다. 그런데 실행 콜백이 도는 동안 취소 요청을 받는 것도 콜백이에요. 5.7절에서 본 것처럼 일꾼이 한 명이면 실행 콜백이 끝날 때까지 취소 요청을 처리하지 못하니, 이 노드는 `MultiThreadedExecutor`로 돌립니다.

```python
"""5.9절: 이동 액션 클라이언트. 끝까지 가기, 너무 먼 목표, 도중에 취소하기를 차례로 해 본다."""
import rclpy
from action_msgs.msg import GoalStatus
from rclpy.action import ActionClient
from rclpy.node import Node
from robot_interfaces.action import MoveTo


def 보내기(노드: Node, 클라이언트: ActionClient, x: float, y: float, 취소_시점: int = 0) -> None:
    """목표를 보내고 결과까지 기다린다. 취소_시점이 있으면 그만큼 피드백을 받은 뒤 취소한다."""
    피드백_수 = 0

    def 피드백_받기(메시지) -> None:
        nonlocal 피드백_수
        피드백_수 += 1
        print(f"  피드백: 남은 거리 {메시지.feedback.remaining:.3f}m")

    미래 = 클라이언트.send_goal_async(MoveTo.Goal(x=x, y=y), feedback_callback=피드백_받기)
    rclpy.spin_until_future_complete(노드, 미래)
    핸들 = 미래.result()                                   # 서버가 목표를 받아들였는가
    print(f"목표 ({x}, {y}) → {'받아들여짐' if 핸들.accepted else '거절됨'}")
    if not 핸들.accepted:
        return
    결과_미래 = 핸들.get_result_async()
    while not 결과_미래.done():
        rclpy.spin_once(노드, timeout_sec=0.1)
        if 피드백_수 == 취소_시점 > 0:
            print("  취소를 요청한다")
            rclpy.spin_until_future_complete(노드, 핸들.cancel_goal_async())
            취소_시점 = 0
    결과 = 결과_미래.result()
    if 결과.status == GoalStatus.STATUS_SUCCEEDED:
        print(f"  성공: 남은 거리 {결과.result.error:.3f}m")
    elif 결과.status == GoalStatus.STATUS_CANCELED:
        print("  취소됨: 그 자리에 섰다")


with rclpy.init():
    노드 = Node("move_client")
    클라이언트 = ActionClient(노드, MoveTo, "move_to")
    클라이언트.wait_for_server(timeout_sec=5.0)
    보내기(노드, 클라이언트, 2.0, 1.0)
    보내기(노드, 클라이언트, 9.0, 9.0)
    보내기(노드, 클라이언트, 0.0, 0.0, 취소_시점=2)
```

클라이언트는 목표를 세 번 보냅니다. (2, 1)까지 끝까지 가기, 너무 먼 (9, 9), 그리고 원점으로 돌아가다가 피드백을 두 번 받으면 취소하기예요. `send_goal_async`가 돌려준 미래에는 서버가 목표를 받아들였는지가 담기고, `get_result_async`의 미래에는 최종 결과가 담깁니다.

```bash
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
```

```text
## 만든 액션 타입
float64 x
float64 y
---
float64 error
---
float64 remaining
## 액션 목록
/move_to [robot_interfaces/action/MoveTo]
## 클라이언트
목표 (2.0, 1.0) → 받아들여짐
  피드백: 남은 거리 1.736m
  피드백: 남은 거리 1.236m
  피드백: 남은 거리 0.736m
  피드백: 남은 거리 0.243m
  피드백: 남은 거리 0.048m
  피드백: 남은 거리 0.009m
  성공: 남은 거리 0.009m
목표 (9.0, 9.0) → 거절됨
목표 (0.0, 0.0) → 받아들여짐
  피드백: 남은 거리 1.727m
  피드백: 남은 거리 1.227m
  취소를 요청한다
  취소됨: 그 자리에 섰다
```

첫 목표의 피드백을 보세요. 1.736, 1.236, 0.736, 0.243, 0.048, 0.009m. 1장 1.1절의 닫힌 고리에서 1초마다 찍었던 남은 거리와 한 자리도 다르지 않습니다. 이번에는 그 계산이 다른 프로세스에서 돌고 결과만 메시지로 건너왔어요. (9, 9)는 서버의 `목표_검사`가 거절했고, 원점으로 가던 셋째 목표는 피드백 두 번 뒤에 취소되어 그 자리에 섰습니다. `ros2 action list -t`로 액션 이름과 타입을 확인할 수 있고, `ros2 action send_goal`로 명령줄에서 목표를 보낼 수도 있어요.

## 5.10 launch: 여러 노드를 한 번에 띄우기

### 터미널 열 개 대신 파일 하나

노드가 셋만 돼도 터미널을 셋 열고, 각각 `source`하고, 파라미터를 붙여 띄우기가 번거롭습니다. 진짜 로봇은 노드가 수십 개예요. 그래서 "어떤 노드를 어떤 설정으로 띄울지"를 파일 하나에 적어 두고 한 번에 띄웁니다. 이 파일이 **launch 파일**이고, 파이썬으로 씁니다. 로봇 두 대의 배터리 노드를 한 번에 띄워 보겠습니다.

```python
"""5.10절: 로봇 두 대의 배터리 노드를 한 번에 띄우는 launch 파일."""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    노드들 = []
    for 로봇 in ["robot1", "robot2"]:                 # 같은 노드를 이름공간만 바꿔 두 벌 띄운다
        노드들.append(Node(package="battery_demo", executable="battery_monitor", namespace=로봇, output="screen"))
        노드들.append(Node(package="battery_demo", executable="battery_publisher", namespace=로봇, output="screen"))
    return LaunchDescription(노드들)
```

launch 파일에는 `generate_launch_description` 함수가 있어야 하고, 이 함수가 띄울 것들의 목록인 `LaunchDescription`을 돌려줍니다. `Node`의 `package`와 `executable`은 `ros2 run`에 주던 두 이름이에요. `namespace`에 `robot1`, `robot2`를 주어 같은 노드를 두 벌 띄웠습니다. `output="screen"`은 노드의 출력을 화면에 보이라는 뜻이고, 주지 않으면 로그 파일에만 남아요.

```bash
source /src/책환경.sh
source /src/패키지만들기.sh
패키지_만들기 battery_demo battery_publisher=배터리발행.py battery_monitor=배터리구독.py
ros2 daemon start > /dev/null
뒤에서 ros2 launch /src/배터리_launch.py > /tmp/launch.txt
sleep 3
echo "## 노드"; ros2 node list
echo "## 토픽"; ros2 topic list | grep battery
kill -INT %1 && wait                       # launch에 Ctrl+C를 보내면 띄운 노드를 모두 끝낸다
echo "## 감시 노드의 출력(노드별로 모아서)"
grep "^\[battery_monitor" /tmp/launch.txt | sort -s -k1,1
```

```text
## 노드
/robot1/battery_monitor
/robot2/battery_monitor
## 토픽
/robot1/battery_voltage
/robot2/battery_voltage
## 감시 노드의 출력(노드별로 모아서)
[battery_monitor-1] [INFO] [robot1.battery_monitor]: 받음: 12.5V
[battery_monitor-1] [INFO] [robot1.battery_monitor]: 받음: 12.3V
[battery_monitor-1] [INFO] [robot1.battery_monitor]: 받음: 12.1V
[battery_monitor-1] [WARN] [robot1.battery_monitor]: 받음: 11.9V, 충전이 필요하다
[battery_monitor-1] [WARN] [robot1.battery_monitor]: 받음: 11.7V, 충전이 필요하다
[battery_monitor-3] [INFO] [robot2.battery_monitor]: 받음: 12.5V
[battery_monitor-3] [INFO] [robot2.battery_monitor]: 받음: 12.3V
[battery_monitor-3] [INFO] [robot2.battery_monitor]: 받음: 12.1V
[battery_monitor-3] [WARN] [robot2.battery_monitor]: 받음: 11.9V, 충전이 필요하다
[battery_monitor-3] [WARN] [robot2.battery_monitor]: 받음: 11.7V, 충전이 필요하다
```

노드 이름이 `/robot1/battery_monitor`, `/robot2/battery_monitor`가 되고, 토픽도 `/robot1/battery_voltage`, `/robot2/battery_voltage`로 갈라졌습니다. 5.3절의 이름 규칙대로 빗금 없이 적은 토픽 이름 `battery_voltage`가 노드의 이름공간 아래에 붙은 거예요. 코드를 한 줄도 고치지 않고 로봇 두 대 몫의 노드를 띄웠고, 두 로봇의 메시지는 섞이지 않습니다. 발행 노드들은 다섯 번 보내고 이미 끝나서 노드 목록에는 감시 노드만 남았어요.

launch는 각 줄 앞에 `[battery_monitor-1]`처럼 **프로세스 이름과 번호**를 붙여 줍니다. 여러 노드의 출력이 한 화면에 섞여도 어느 노드의 말인지 알 수 있게요. 실제 출력에서는 두 로봇의 줄이 도착한 순서대로 뒤섞여 나오는데, 그 순서는 실행할 때마다 달라서 책에서는 노드별로 모아(`sort -s -k1,1`) 보였습니다. launch에 Ctrl+C를 보내면 띄운 노드들에게 차례로 Ctrl+C를 전하고 모두 끝날 때까지 기다려 줘요.

## 5.11 실습: 점 로봇을 세 노드로

### 무엇을 만드나

1장의 점 로봇은 고리 하나가 감지·판단·행동을 모두 했습니다. 이제 그 셋을 ROS 2 노드 셋으로 나눠 토픽으로 이어 보겠습니다.

| 노드 | 맡은 일 | 받는 토픽 | 보내는 토픽 | 1장의 무엇 |
|---|---|---|---|---|
| `position_sensor` | 감지 | `true_position` | `measured_position` | `위치_재기` |
| `judge` | 판단 | `measured_position` | `cmd_vel` | `이득 * (목표 - 잰_위치)` |
| `simulator` | 행동(과 세상) | `cmd_vel` | `true_position` | `움직이기` |

시뮬레이터 노드가 진짜 세상 노릇을 합니다. 진짜 위치를 `true_position`으로 알리면 센서 노드가 잡음을 섞어 `measured_position`으로 내보내고, 판단 노드는 잰 위치만 보고 `cmd_vel`을 내요. 판단 노드가 진짜 위치를 볼 방법이 아예 없다는 점이 1장보다 확실해졌죠. 진짜 로봇에서는 시뮬레이터 자리에 모터 드라이버와 센서 드라이버 노드를 끼우면 됩니다.

### 결과가 매번 같도록

노드 셋이 따로 돌면 메시지가 도착하는 때에 따라 결과가 조금씩 달라집니다. 이득에 따른 차이를 비교하려면 매번 같은 결과가 나와야 하니, 이 실습의 시뮬레이터는 판단 노드의 명령이 올 때까지 기다렸다가 한 걸음을 가게 했습니다. 시뮬레이션 시각을 메시지의 `stamp`에 적어 보내고, 명령에도 어느 측정을 보고 낸 명령인지 같은 시각을 붙여 돌려받아요. 시각이 맞지 않는 명령은 버립니다. 잡음과 미끄러짐도 시각과 걸음 번호로 난수를 정해서, 같은 걸음에서는 늘 같은 값이 나와요. 이렇게 시뮬레이터가 제어와 발맞춰 한 걸음씩 가는 방식을 **록스텝(lockstep)** 이라고 합니다.

세 노드는 패키지 `point_robot` 안에서 1장의 `점로봇.py`를 `point_robot.점로봇`으로 가져다 씁니다. 그래서 이 파일들은 패키지로 빌드한 뒤에만 실행할 수 있어요.

```python
"""5.11절 실습, 감지: 진짜 위치를 받아 잡음 섞인 측정값으로 내보내는 위치 센서 노드."""
import numpy as np
import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.time import Time

from point_robot.점로봇 import 위치_재기


class 위치센서(Node):
    def __init__(self):
        super().__init__("position_sensor")
        self.잡음 = self.declare_parameter("noise", 0.0).value       # m
        self.씨앗 = self.declare_parameter("seed", 1).value
        self.발행자 = self.create_publisher(PointStamped, "measured_position", 10)
        self.create_subscription(PointStamped, "true_position", self.재기, 10)

    def 재기(self, 진짜: PointStamped) -> None:
        # 같은 시각의 측정은 몇 번을 다시 재도 같은 잡음이 나오게 시각으로 난수를 정한다
        생성기 = np.random.default_rng([self.씨앗, Time.from_msg(진짜.header.stamp).nanoseconds])
        잰_위치 = 위치_재기(np.array([진짜.point.x, 진짜.point.y]), 생성기, self.잡음)
        잰 = PointStamped()
        잰.header = 진짜.header                                     # 언제, 어느 좌표계로 잰 값인지 그대로
        잰.point.x, 잰.point.y = float(잰_위치[0]), float(잰_위치[1])
        self.발행자.publish(잰)


def main() -> None:
    try:
        with rclpy.init():
            rclpy.spin(위치센서())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
```

센서 노드는 받은 진짜 위치에 1장의 `위치_재기`로 잡음을 섞습니다. 머리말은 그대로 복사해서, 언제 어느 좌표계로 잰 값인지가 따라가게 했어요.

```python
"""5.11절 실습, 판단: 잰 위치를 받아 비례 제어로 속도 명령을 내는 노드."""
import numpy as np
import rclpy
from geometry_msgs.msg import PointStamped, TwistStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class 판단(Node):
    def __init__(self):
        super().__init__("judge")
        self.declare_parameter("gain", 1.5)                 # 남은 거리 1m당 몇 m/s로 갈까
        self.declare_parameter("goal", [2.0, 1.0])          # 목표 위치(m)
        self.발행자 = self.create_publisher(TwistStamped, "cmd_vel", 10)
        self.create_subscription(PointStamped, "measured_position", self.판단하기, 10)

    def 판단하기(self, 잰: PointStamped) -> None:
        이득 = self.get_parameter("gain").value            # 매번 읽으니 도는 중에 바꿔도 바로 반영된다
        목표 = np.array(self.get_parameter("goal").value)
        속도 = 이득 * (목표 - np.array([잰.point.x, 잰.point.y]))
        명령 = TwistStamped()
        명령.header.stamp = 잰.header.stamp                 # 어느 측정을 보고 낸 명령인지 표시한다
        명령.twist.linear.x, 명령.twist.linear.y = float(속도[0]), float(속도[1])
        self.발행자.publish(명령)


def main() -> None:
    try:
        with rclpy.init():
            rclpy.spin(판단())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
```

판단 노드는 콜백이 불릴 때마다 `gain`과 `goal` 파라미터를 새로 읽습니다. 그래서 도는 중에 `ros2 param set /judge gain 4.0`처럼 바꾸면 다음 판단부터 바로 반영돼요. 속도 제한은 판단 노드가 아니라 시뮬레이터의 `움직이기` 안에 있습니다. 1장처럼 모터가 낼 수 있는 속도의 한계는 몸의 성질이니까요. 이 점 로봇은 옆으로도 바로 갈 수 있어서 `linear.y`까지 쓰는데, 바퀴 둘 달린 실제 이동 로봇은 `linear.x`와 `angular.z`만 씁니다.

```python
"""5.11절 실습, 행동: 속도 명령을 받아 점 로봇을 한 걸음씩 움직이는 시뮬레이터 노드."""
import numpy as np
import rclpy
from geometry_msgs.msg import PointStamped, TwistStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.time import Time

from point_robot.점로봇 import 움직이기


class 시뮬레이터(Node):
    def __init__(self):
        super().__init__("simulator")
        self.주기 = self.declare_parameter("period", 0.1).value       # 한 걸음의 시뮬레이션 시간(초)
        self.걸음_수 = self.declare_parameter("steps", 80).value
        self.미끄러짐 = self.declare_parameter("slip", 0.0).value
        self.기록_파일 = self.declare_parameter("record", "").value  # 경로를 남길 CSV 파일 이름
        self.걸음, self.위치 = 0, np.array([0.0, 0.0])
        self.경로 = [self.위치]
        self.발행자 = self.create_publisher(PointStamped, "true_position", 10)
        self.create_subscription(TwistStamped, "cmd_vel", self.명령_받기, 10)
        self.지난_걸음 = -1
        self.create_timer(0.5, self.멈췄으면_다시_알리기)

    def 지금_시각(self) -> int:
        return round(self.걸음 * self.주기 * 1e9)                   # 시뮬레이션 시각(나노초)

    def 위치_알리기(self) -> None:
        메시지 = PointStamped()
        메시지.header.stamp = Time(nanoseconds=self.지금_시각()).to_msg()
        메시지.header.frame_id = "world"
        메시지.point.x, 메시지.point.y = float(self.위치[0]), float(self.위치[1])
        self.발행자.publish(메시지)

    def 멈췄으면_다시_알리기(self) -> None:
        # 처음 연결될 때처럼 메시지가 사라져 0.5초 동안 한 걸음도 못 갔으면 지금 위치를 다시 알린다
        if self.걸음 == self.지난_걸음:
            self.위치_알리기()
        self.지난_걸음 = self.걸음

    def 명령_받기(self, 명령: TwistStamped) -> None:
        if Time.from_msg(명령.header.stamp).nanoseconds != self.지금_시각():
            return                                                  # 지난 걸음에 대한 명령은 버린다
        생성기 = np.random.default_rng([7, self.걸음])                # 걸음마다 정해진 미끄러짐
        속도 = np.array([명령.twist.linear.x, 명령.twist.linear.y])
        self.위치 = 움직이기(self.위치, 속도, self.주기, 생성기, self.미끄러짐)
        self.걸음 += 1
        self.경로.append(self.위치)
        if self.걸음 % 10 == 0:
            self.get_logger().info(f"{self.걸음 * self.주기:.1f}초: 위치 {np.round(self.위치, 3)}")
        if self.걸음 < self.걸음_수:
            self.위치_알리기()
        else:
            self.끝내기()

    def 끝내기(self) -> None:
        if self.기록_파일:
            np.savetxt(self.기록_파일, np.array(self.경로), delimiter=",", header="x,y", comments="")
        self.get_logger().info(f"{self.걸음}걸음 끝. 마지막 위치 {np.round(self.위치, 3)}")
        rclpy.shutdown()


def main() -> None:
    try:
        with rclpy.init():
            rclpy.spin(시뮬레이터())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
```

시뮬레이터는 명령을 받을 때마다 한 걸음 움직이고, 1초(10걸음)마다 위치를 로그로 남기고, 걸음 수를 채우면 경로를 CSV로 저장한 뒤 끝납니다. `멈췄으면_다시_알리기`는 노드끼리 막 연결되는 동안 첫 메시지가 사라질 때를 대비한 장치예요. 같은 걸음을 두 번 알려도 그 시각의 명령은 한 번만 받고 잡음도 같으니 결과는 그대로입니다.

```python
"""5.11절 실습: 센서·판단·시뮬레이터 세 노드를 한 번에 띄운다."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def 실수_인자(이름: str) -> ParameterValue:
    """명령줄에서 받은 글자를 실수 파라미터로 넘긴다(gain:=2처럼 정수로 적어도 2.0이 된다)."""
    return ParameterValue(LaunchConfiguration(이름), value_type=float)


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription([
        DeclareLaunchArgument("gain", default_value="1.5"),       # ros2 launch ... gain:=4.0 처럼 바꾼다
        DeclareLaunchArgument("noise", default_value="0.0"),
        DeclareLaunchArgument("slip", default_value="0.0"),
        DeclareLaunchArgument("record", default_value=""),
        Node(package="point_robot", executable="sensor", output="screen",
             parameters=[{"noise": 실수_인자("noise")}]),
        Node(package="point_robot", executable="judge", output="screen",
             parameters=[{"gain": 실수_인자("gain")}]),
        Node(package="point_robot", executable="simulator", output="screen",
             parameters=[{"slip": 실수_인자("slip"), "record": LaunchConfiguration("record")}],
             on_exit=Shutdown()),                                  # 시뮬레이터가 끝나면 모두 끝낸다
    ])
```

launch 파일에 `DeclareLaunchArgument`로 인자 넷을 선언했습니다. `ros2 launch /src/점로봇_launch.py gain:=4.0`처럼 명령줄에서 바꿀 수 있고, `--show-args`를 붙이면 받을 수 있는 인자 목록이 나와요. 인자는 글자로 들어오는데, `gain:=2`처럼 소수점 없이 적으면 정수 2가 되어 실수 파라미터 `gain`과 타입이 맞지 않습니다. 실제로 `ParameterValue` 없이 넘겨 `gain:=2`로 띄우면 판단 노드가 `declare_parameter`에서 오류를 내고 죽어요. 그래서 `실수_인자`로 감싸 늘 실수로 넘겼습니다. 시뮬레이터 노드에 단 `on_exit=Shutdown()`은 시뮬레이터가 끝나면 나머지 노드도 모두 끝내라는 뜻입니다.

### 1장과 같은 답인가

먼저 잡음과 미끄러짐 없이, 1장 1.1절의 닫힌 고리와 같은 조건(이득 1.5, 주기 0.1초, 80걸음)으로 돌려 봅시다. 시뮬레이터의 로그만 골라 봅니다.

```bash
source /src/책환경.sh
source /src/패키지만들기.sh
패키지_만들기 point_robot 점로봇.py sensor=센서노드.py judge=판단노드.py simulator=시뮬레이터노드.py
ros2 launch /src/점로봇_launch.py | grep "^\[simulator" | sed 's/^\[simulator-3\] //'
```

```text
[INFO] [simulator]: 1.0초: 위치 [0.447 0.224]
[INFO] [simulator]: 2.0초: 위치 [0.894 0.447]
[INFO] [simulator]: 3.0초: 위치 [1.342 0.671]
[INFO] [simulator]: 4.0초: 위치 [1.783 0.891]
[INFO] [simulator]: 5.0초: 위치 [1.957 0.979]
[INFO] [simulator]: 6.0초: 위치 [1.992 0.996]
[INFO] [simulator]: 7.0초: 위치 [1.998 0.999]
[INFO] [simulator]: 8.0초: 위치 [2. 1.]
[INFO] [simulator]: 80걸음 끝. 마지막 위치 [2. 1.]
```

1.0초 [0.447 0.224], 2.0초 [0.894 0.447], ..., 8.0초 [2. 1.]. 1장 1.1절의 출력과 **한 글자도 다르지 않습니다**. 감지·판단·행동을 세 프로세스로 쪼개고 한 걸음에 메시지가 세 번씩 오갔지만, 계산은 똑같이 이어졌어요.

### 이득 바꿔 보기

이번에는 1장처럼 센서 잡음 0.02m와 미끄러짐 0.2를 넣고, 판단 노드의 이득만 0.5, 1.5, 12로 바꿔 세 번 돌립니다. 다른 노드는 손대지 않고 launch 인자 하나만 바꾸는 거예요.

```bash
source /src/책환경.sh
source /src/패키지만들기.sh
패키지_만들기 point_robot 점로봇.py sensor=센서노드.py judge=판단노드.py simulator=시뮬레이터노드.py
for gain in 0.5 1.5 12.0; do                    # 이득만 바꿔 세 번 돌리고, 경로를 CSV로 남긴다
    echo "## 이득 $gain"
    ros2 launch /src/점로봇_launch.py gain:=$gain noise:=0.02 slip:=0.2 record:=path_gain_$gain.csv \
        | grep "^\[simulator" | sed 's/^\[simulator-3\] //' | tail -1
done
```

```text
## 이득 0.5
[INFO] [simulator]: 80걸음 끝. 마지막 위치 [1.908 0.995]
## 이득 1.5
[INFO] [simulator]: 80걸음 끝. 마지막 위치 [1.996 1.005]
## 이득 12.0
[INFO] [simulator]: 80걸음 끝. 마지막 위치 [2.021 1.001]
```

시뮬레이터가 남긴 CSV 파일 세 개는 `-v`로 연결한 장 폴더에 생겼으니, 컨테이너 밖 맥에서 1~4장과 같은 uv 환경으로 그림을 그립니다. 컨테이너 이미지에는 matplotlib을 넣지 않았거든요. 로봇 쪽 컴퓨터는 기록만 하고, 분석과 그림은 내 컴퓨터에서 하는 것도 흔한 나눔입니다.

```python
# 맥(호스트)에서 실행: 컨테이너가 남긴 CSV를 읽어 그린다
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

목표 = np.array([2.0, 1.0])
주기 = 0.1
그림, (왼쪽, 오른쪽) = plt.subplots(1, 2, figsize=(9.5, 3.8))
for 이득, 색 in [("0.5", "tab:green"), ("1.5", "tab:blue"), ("12.0", "tab:red")]:
    경로 = np.loadtxt(f"path_gain_{이득}.csv", delimiter=",", skiprows=1)    # 첫 줄은 열 이름
    거리 = np.linalg.norm(경로 - 목표, axis=1)
    시간 = np.arange(len(경로)) * 주기
    왼쪽.plot(경로[:, 0], 경로[:, 1], "o-", markersize=2, color=색, label=f"이득 {이득}")
    오른쪽.plot(시간, 거리, color=색, label=f"이득 {이득}")
    print(f"이득 {이득:>4s}: 8초 뒤 남은 거리 {거리[-1]:.3f}m, 마지막 2초 평균 {거리[-20:].mean():.3f}m, "
          f"가장 멀 때 {거리[-20:].max():.3f}m")
왼쪽.scatter(*목표, marker="*", s=250, color="gold", edgecolors="black", zorder=5, label="목표")
왼쪽.set_xlim(1.7, 2.1)                          # 목표 근처만 크게 본다
왼쪽.set_ylim(0.85, 1.1)
왼쪽.set_xlabel("x (m)")
왼쪽.set_ylabel("y (m)")
왼쪽.set_aspect("equal")
왼쪽.set_title("목표 근처의 경로")
왼쪽.legend(loc="lower right", fontsize=8)
오른쪽.set_ylim(0, 0.5)
오른쪽.set_xlabel("시간(초)")
오른쪽.set_ylabel("목표까지 남은 거리(m)")
오른쪽.set_title("남은 거리")
오른쪽.legend(fontsize=8)
그림.tight_layout()
그림.savefig("ros_point_robot.png", dpi=200)
print("저장: ros_point_robot.png")
```

```text
이득  0.5: 8초 뒤 남은 거리 0.092m, 마지막 2초 평균 0.146m, 가장 멀 때 0.217m
이득  1.5: 8초 뒤 남은 거리 0.006m, 마지막 2초 평균 0.013m, 가장 멀 때 0.026m
이득 12.0: 8초 뒤 남은 거리 0.021m, 마지막 2초 평균 0.023m, 가장 멀 때 0.043m
저장: ros_point_robot.png
```

![이득 0.5, 1.5, 12로 돌린 점 로봇. 왼쪽은 목표 근처의 경로로, 이득 12(빨강)는 목표 주위를 이리저리 튀고 이득 1.5(파랑)는 목표 가까이 모인다. 오른쪽은 목표까지 남은 거리로, 이득 0.5(초록)는 8초가 지나도 0.1m 가까이 남고, 이득 12는 가장 먼저 다가가지만 0.02m 안팎에서 계속 흔들린다.](../assets/images/ch05/ros_point_robot.png)

세 이득의 성격이 뚜렷하게 갈립니다.

- **이득 0.5**: 굼뜹니다. 남은 거리 1m당 0.5m/s만 내니 가까워질수록 너무 천천히 다가가서, 8초가 지나도 0.092m가 남았어요.
- **이득 1.5**: 1장에서 쓴 값입니다. 5초 남짓에 목표 근처에 와서 마지막 2초 동안 평균 0.013m 안에 머물렀어요.
- **이득 12**: 가장 빨리 다가가지만 도착한 뒤가 문제입니다. 마지막 2초 평균이 0.023m로 이득 1.5보다 오히려 컸고, 가장 멀 때는 0.043m까지 튀었어요. 센서가 2cm쯤 틀리면 판단 노드는 그 오차에 12를 곱한 0.24m/s로 "고치러" 달려가니, 잡음을 그대로 키워 버린 겁니다. 1장 1.4절의 기준으로 보면 이득 × 주기가 1.2로 1을 넘어서, 한 번에 남은 거리보다 더 많이 고치는 영역이기도 해요.

이득은 크면 빠르지만 잡음과 지나침에 약하고, 작으면 차분하지만 굼뜹니다. 이 균형을 체계적으로 잡는 방법은 12장에서 배워요. 여기서 기억할 것은 이 실험을 **판단 노드의 파라미터 하나만 바꿔서** 했다는 점입니다. 센서 노드를 진짜 드라이버로, 시뮬레이터를 4장의 MuJoCo로 바꿔도 판단 노드는 그대로 쓸 수 있어요.

## 5.12 정리와 다음 장 미리보기

이 장에서 로봇 프로그램을 여러 조각으로 나누고 잇는 방법을 익혔습니다.

- **왜 나누나**: 한 고리에 다 넣으면 느린 일이 급한 일의 박자를 정하고, 한 곳의 오류가 전체를 멈춘다. 역할별 노드가 메시지를 주고받으면 박자와 고장이 분리되고 부품을 끼우기 쉽다
- **ROS 2**: 운영 체제가 아니라 통신·도구·생태계. 이 책은 Lyrical Luth(우분투 26.04, 파이썬 3.14), 밑에는 DDS. 맥·윈도우는 Docker로
- **노드**: `Node`를 물려받고, 타이머·구독에 콜백을 맡기고, `spin`으로 기다린다. 로그는 `get_logger()`, 노드·토픽 이름은 영문자·숫자·밑줄
- **토픽**: 발행자와 구독자가 이름과 메시지 타입만 맞추면 연결된다. `ros2 topic list/info/echo/hz/pub`로 들여다본다. 실수 칸에 정수를 넣으면 발행할 때 프로세스가 죽는다(`ROS_PYTHON_CHECK_FIELDS=1`)
- **QoS**: 발행자의 약속이 구독자의 요구 이상이어야 연결된다(`BEST_EFFORT` 발행 + `RELIABLE` 구독은 연결 안 됨). 깊이는 쌓아 둘 개수, `TRANSIENT_LOCAL`은 늦게 온 구독자에게 최근 것을 준다
- **서비스와 액션**: 금방 끝나는 요청·응답은 서비스, 오래 걸리고 피드백·취소가 필요한 일은 액션. 콜백 안에서는 `call` 대신 `call_async`
- **파라미터**: `declare_parameter`로 꺼낸 설정 손잡이. 명령줄·파일로 바꾸고, 검사 함수는 선언보다 먼저 건다
- **시간**: 기본 실행기는 콜백을 하나씩 부르니 무거운 콜백은 따로 떼거나 콜백 그룹과 다중 스레드 실행기를 쓴다. 메시지에는 `stamp`와 `frame_id`를 붙이고, 시뮬레이션에서는 `/clock`과 `use_sim_time`
- **패키지와 launch**: ament_python 패키지의 `entry_points`로 실행 파일을 만들고 colcon으로 빌드한다. 액션 타입은 ament_cmake 인터페이스 패키지로. launch 파일로 여러 노드를 이름공간·파라미터·인자와 함께 띄운다
- **실습**: 점 로봇을 감지·판단·행동 세 노드로 나눠도 1장과 같은 답이 나왔다. 판단 노드의 이득 하나만 바꿔 굼뜬 로봇과 떠는 로봇을 비교했다

그런데 이 장의 로봇은 여전히 평면 위의 점이었습니다. 진짜 로봇은 부품마다 2장의 좌표계가 하나씩 붙어 있어서, 카메라가 본 컵을 팔의 좌표로 바꾸려면 그 좌표계들이 어떻게 이어져 있는지 누군가 알고 있어야 하죠. 다음 6장에서는 로봇의 몸을 **URDF**라는 파일로 적고, ROS 2가 그 파일에서 좌표계 사이의 관계를 계산해 tf2로 알려 주게 한 뒤, 로봇의 모습을 눈으로 확인합니다. 3장의 관절과 링크가 이번에는 ROS 2의 노드와 토픽 위에서 움직이는 거예요.
