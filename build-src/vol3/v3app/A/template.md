# 부록 A. 실행 환경: uv, MuJoCo, ROS 2 Docker

새 컴퓨터에서 3권의 예제를 처음 돌려 보려는 참이라고 해 봅시다. 무엇부터 준비해야 할까요? 1권은 파이썬과 uv면 충분했고, 2권은 여기에 PyTorch와 그래픽 카드 이야기가 더해졌습니다. 3권은 준비물이 두 갈래예요. 하나는 1~4장과 7~20장의 대부분이 쓰는 **파이썬 환경**(MuJoCo, NumPy, OpenCV, PyTorch 등)이고, 다른 하나는 5·6장이 쓰는 **ROS 2 Lyrical이 든 Docker 상자**입니다. 두 환경은 파이썬 버전도 다르고 사는 곳도 달라서, 어느 코드가 어디서 도는지 헷갈리기 쉬워요.

이 부록은 그 준비를 한곳에 모았습니다. 고정한 패키지 버전, 맥·윈도우·리눅스별 준비, 화면 없이 MuJoCo로 사진 찍기와 대화형 뷰어, ROS 2 Docker 이미지 만들기와 쓰기, 여러 컨테이너가 섞이지 않게 하는 방법, 내려받는 모델과 사진의 위치와 라이선스, 19장 선택 절의 API 키, 그리고 자주 만나는 설치 문제까지 다룹니다. 처음 시작할 때 한 번 훑어보고, 문제가 생겼을 때 다시 펼쳐 보세요.

이 부록의 명령과 출력은 이 책을 쓴 컴퓨터(Apple M4 Max 맥북, macOS, uv 0.9.16, Docker 28.3)에서 직접 실행해 확인했습니다. 리눅스에서의 MuJoCo 렌더링은 같은 컴퓨터의 우분투 24.04 컨테이너 안에서 확인했고, 윈도우에 관한 내용은 Docker와 MuJoCo의 공식 안내를 따랐어요. 2026년 10월에 확인한 내용이라, 여러분이 읽을 때는 버전 번호가 바뀌어 있을 수 있습니다.

---

## A.1 예제 환경과 고정한 버전

### pyproject.toml 한 장

3권의 예제는 `examples/vol3` 폴더 하나에 들어 있고, 그 폴더의 `pyproject.toml`이 필요한 패키지와 버전을 정확히 적어 둡니다. 1장 1.6절에서 본 것처럼 `uv sync` 한 번이면 본문 출력을 만든 것과 똑같은 버전이 설치돼요.

| 패키지 | 고정한 버전 | 처음 쓰는 장 | 하는 일 |
|---|---|---|---|
| 파이썬 | 3.12 (`>=3.12,<3.13`) | 1장 | |
| `mujoco` | 3.17.0 | 1장 | 물리 시뮬레이션과 렌더링 |
| `numpy` | 2.5.4 | 1장 | 배열 계산 |
| `matplotlib` | 3.11.2 | 1장 | 그림 그리기(Pillow가 함께 설치됨) |
| `scipy` | 1.18.1 | 2장 | 회전 변환, 최적화, 최소제곱 |
| `pyserial` | 3.5 | 7장 | 직렬 포트(서보 버스) |
| `opencv-python-headless` | 5.0.0.93 | 9장 | 카메라 보정, 색 분할, ArUco |
| `torch` | 2.14.1 | 9장 | 신경망(2권과 같은 판) |
| `torchvision` | 0.29.1 | 9장 | 사전학습 검출기·자세 추정 모델 |
| `gymnasium[mujoco]` | 1.4.0 | 17장 | 강화 학습 환경 |
| `transformers` | 5.20.2 | 19장 | 비전-언어 모델, 언어 모델 |
| `anthropic` | 2.3.0 | 19장 | Claude API(선택 절) |

`opencv-python-headless`는 창을 띄우는 기능(`cv2.imshow`)을 뺀 OpenCV입니다. 이 책은 결과를 모두 파일로 저장하니 창이 필요 없고, 화면 없는 서버에서도 그대로 설치돼요. 같은 환경에 `opencv-python`(창 있는 판)을 함께 설치하면 둘이 같은 `cv2`를 덮어써서 꼬이니 하나만 고르세요.

```bash
cd examples/vol3
uv sync                      # 파이썬 3.12가 없으면 uv가 내려받고, 잠금 파일(uv.lock)대로 설치한다
uv run python 01-what-is-a-robot/b03_closed_loop.py
```

`uv sync`는 `uv.lock`에 적힌 판을 그대로 설치합니다. 이 책을 쓴 맥에서 처음 설치하면 PyTorch와 transformers 때문에 수 GB를 내려받으니 시간이 조금 걸려요. uv 설치와 `uv sync`, `uv run`의 자세한 쓰임은 1권 부록 A에 있습니다.

### 설치 확인

설치가 끝났으면 버전과 장치를 한 번에 확인해 봅시다.

<<CODE a01_versions_host>>

<<OUT a01_versions_host>>

표와 같은 버전이 찍히면 됩니다. 마지막 줄은 9장 이후 신경망이 쓸 장치예요. 이 맥에는 NVIDIA 그래픽 카드가 없어 CUDA는 False, 애플 실리콘의 MPS는 True입니다. 3권의 신경망 예제는 결과를 고정하려고 CPU로 돌린 것이 많아서 어느 쪽이든 실행에는 문제가 없어요. PyTorch를 NVIDIA GPU용으로 설치하는 방법은 2권 부록 A를 보세요.

> **Q. 표와 버전이 조금 달라도 되나요?**
> 대부분의 예제는 그대로 돌아갑니다. 다만 시뮬레이션은 판이 바뀌면 접촉 계산이나 기본값이 조금씩 달라질 수 있어서, 소수점 아래 숫자나 학습 곡선이 본문과 어긋날 수 있어요. 본문과 숫자를 한 자리까지 맞춰 보고 싶다면 `examples/vol3`에서 `uv sync`로 잠금 파일 그대로 설치하세요.

## A.2 운영체제별 준비

3권은 **맥, 윈도우, 리눅스 어디서나** 시뮬레이션만으로 끝까지 따라올 수 있습니다(1장 1.6절의 약속). 운영체제마다 다른 것은 두 가지, MuJoCo의 화면 처리와 Docker를 까는 방법이에요.

| | 맥 | 윈도우 | 리눅스(우분투 등) |
|---|---|---|---|
| uv와 예제 환경 | `uv sync` | `uv sync` | `uv sync` |
| 화면 없이 렌더링 | 그대로 됨(CGL) | 데스크톱에서는 그대로 됨 | 화면 없는 서버는 `MUJOCO_GL=egl` 또는 `osmesa`(A.3절) |
| 대화형 뷰어 코드 | `mjpython`으로 실행 | `python` | `python` |
| ROS 2(5·6장) | Docker Desktop | Docker Desktop(WSL 2) | Docker Engine, 또는 ROS 2를 직접 설치 |
| 서보 키트(7장) | USB 직렬 포트 `/dev/tty.usbmodem...` | `COM3` 같은 포트 | `/dev/ttyACM0`, 사용자에게 포트 권한 필요 |

### 맥

애플 실리콘 맥과 인텔 맥 모두 `uv sync`로 끝납니다. MuJoCo는 맥에서 화면 없이 사진 찍기가 기본으로 되고, 대화형 뷰어를 자기 코드에서 띄울 때만 `mjpython`이라는 전용 실행기가 필요해요(A.3절). ROS 2를 쓰려면 Docker Desktop for Mac을 설치하고 실행해 두세요. 애플 실리콘에서는 이미지가 arm64용으로 만들어집니다. ROS 2 공식 이미지 `ros:lyrical-ros-base`가 amd64와 arm64를 모두 제공하기 때문에 따로 할 일은 없어요.

### 윈도우

파이썬 쪽은 맥과 같습니다. PowerShell에서 uv를 설치하고 `uv sync`를 하면 돼요. ROS 2는 Docker Desktop for Windows로 씁니다. Docker 공식 안내에 따르면 기본 백엔드는 **WSL 2**(윈도우 안의 리눅스)이고, BIOS·UEFI에서 하드웨어 가상화가 켜져 있어야 해요. 설치 조건(윈도우 판, 메모리 등)은 판마다 바뀌니 Docker 문서의 Windows 설치 안내를 확인하세요. 명령은 맥과 거의 같은데, 장 폴더를 연결하는 `-v` 옵션의 현재 폴더 표기만 다릅니다(A.4절).

### 리눅스

우분투 같은 리눅스에서는 Docker Desktop 대신 **Docker Engine**만 설치해도 됩니다. 우분투 26.04라면 ROS 2 Lyrical을 컨테이너 없이 바로 설치할 수도 있는데, 이 경우 ROS 쪽 파이썬은 시스템 파이썬(3.14)이고 `examples/vol3`의 uv 환경(3.12)과는 따로라는 점을 기억하세요. 이 책의 출력과 맞추려면 컨테이너를 쓰는 편이 간단합니다. 화면 없는 서버에서 MuJoCo로 사진을 찍으려면 A.3절의 `MUJOCO_GL`을 설정해야 해요.

> **Q. Docker Desktop은 무료인가요?**
> Docker의 라이선스 안내(2026년 10월 확인)에 따르면 개인 사용, 교육, 비상업 오픈 소스 프로젝트, 그리고 직원 250명 미만이면서 연 매출 1천만 달러 미만인 작은 회사에서는 무료로 쓸 수 있습니다. 그보다 큰 회사에서 업무로 쓰려면 유료 구독이 필요해요. 리눅스의 Docker Engine은 이 조건과 별개입니다. 조건은 바뀔 수 있으니 회사에서 쓴다면 Docker 문서의 라이선스 안내를 직접 확인하세요.

## A.3 MuJoCo 렌더링: 화면 없이, 그리고 뷰어로

### 화면 없이 사진 찍기

이 책의 그림은 모두 `mujoco.Renderer`로 **창을 띄우지 않고** 찍었습니다. 사진이 NumPy 배열로 나오니 그대로 저장하거나 9장처럼 비전 코드에 넣을 수 있죠. 내 컴퓨터에서 이것이 되는지 먼저 확인해 봅시다.

<<CODE a02_render_host>>

<<OUT a02_render_host>>

![화면 없이 찍은 확인용 사진. 회색 바닥 위에 빨간 공이 그림자와 함께 보인다.](../assets/images/appA/render_check.png)

첫 줄의 `mujoco.cgl`은 MuJoCo가 맥의 CGL이라는 방식으로 화면 없이 그림을 그렸다는 뜻입니다. 사진이 (120, 160, 3) 모양으로 나왔고 빨간 공이 359픽셀에 찍혔어요. 이 블록이 오류 없이 돌면 1장부터 20장까지의 렌더링 예제가 모두 됩니다.

MuJoCo가 그림을 그릴 방식은 환경 변수 `MUJOCO_GL`로 고릅니다. MuJoCo 3.17의 소스(`gl_context.py`)를 보면 운영체제마다 받는 값이 정해져 있어요.

| 운영체제 | 정하지 않았을 때 | 고를 수 있는 값 |
|---|---|---|
| 맥 | CGL(화면 없이 됨) | `cgl`, `glfw` |
| 윈도우 | GLFW | `glfw`, `wgl` |
| 리눅스 | GLFW(화면이 있어야 함) | `glfw`, `glx`, `egl`, `osmesa` |

리눅스가 함정입니다. 기본값인 GLFW는 화면(X 서버)이 있어야 해서, 화면 없는 서버나 컨테이너에서는 렌더러를 만드는 순간 실패해요. 이 책의 컴퓨터에서 우분투 24.04 컨테이너에 MuJoCo 3.17.0을 설치해 위와 같은 장면을 찍어 보니, 아무것도 정하지 않으면 `FatalError: an OpenGL platform library has not been loaded into this process...`로 멈췄고, `MUJOCO_GL=egl`과 `MUJOCO_GL=osmesa`는 둘 다 맥과 같은 평균 밝기 106.8의 사진을 냈습니다. `egl`은 그래픽 카드(주로 NVIDIA)로, `osmesa`는 CPU로 그려서 느리지만 어디서나 됩니다. 각각 시스템 라이브러리가 필요한데, 그 컨테이너에서는 우분투 패키지 `libegl1`과 `libosmesa6`을 설치했어요.

```bash
# 화면 없는 리눅스 서버에서
export MUJOCO_GL=egl          # 그래픽 카드가 있으면
export MUJOCO_GL=osmesa       # 없으면(느리지만 CPU로)
uv run python 04-mujoco-basics/b11_render.py
```

### 대화형 뷰어와 mjpython

장면을 처음 만들 때는 마우스로 돌려 보며 고치는 것이 훨씬 빠릅니다. 4장 4.4절에서 소개한 대화형 뷰어는 화면이 있는 컴퓨터에서 이렇게 열어요. 창을 띄우는 프로그램이라 이 책에는 출력을 싣지 않았습니다.

```bash
uv run python -m mujoco.viewer                     # 빈 뷰어. XML 파일을 끌어다 놓는다
uv run python -m mujoco.viewer --mjcf=arm.xml      # XML 파일을 바로 연다
uv run mjpython 내코드.py                          # 맥: launch_passive를 쓰는 내 코드
```

자기 코드에서 시뮬레이션을 돌리며 창을 띄우는 `mujoco.viewer.launch_passive`는 맥에서만 특별 대우가 필요합니다. 맥은 창을 그리는 일을 프로그램의 첫 스레드에서만 하게 하는데, `mjpython`이 그 자리를 뷰어에게 내주고 내 코드를 다른 스레드에서 돌려 주는 실행기예요. 평소처럼 `python`으로 실행하면 어떻게 되는지 봅시다. 창이 열리기 전에 오류가 나니 화면 없는 환경에서도 확인할 수 있습니다.

<<CODE a03_viewer_mac_host>>

<<OUT a03_viewer_mac_host>>

오류 문장이 해결책까지 알려 줍니다. 맥에서는 `uv run mjpython 내코드.py`로 실행하세요. `mjpython`은 `mujoco` 패키지와 함께 가상 환경의 `bin` 폴더에 설치돼 있어요. 윈도우와 리눅스에서는 `python`으로 그대로 됩니다. `python -m mujoco.viewer`로 여는 독립 뷰어는 맥에서도 `python`으로 됩니다.

## A.4 ROS 2 Lyrical Docker 환경

### 이미지 설계도

5장 5.1절에서 본 대로, ROS 2는 **Docker** 상자 안에 우분투 26.04와 ROS 2 Lyrical Luth를 담아 실습합니다. 설계도는 `examples/vol3/ros/Dockerfile`이에요.

<<FILE Dockerfile dockerfile>>

ROS 2 공식 이미지 `ros:lyrical-ros-base`(우분투 26.04, ROS 2의 통신·명령줄 도구)에서 출발해, 5장의 NumPy·SciPy와 6장의 URDF 도구(`robot_state_publisher`, `joint_state_publisher`, `tf2_ros_py`, `xacro`, `urdfdom_py`)를 더 설치합니다. 마지막 두 줄은 컨테이너를 띄우면 ROS 2 환경을 불러오는 공식 시작 스크립트를 거쳐 bash로 들어가게 해요.

### 만들고 들어가기

이미지는 처음 한 번만 만들면 됩니다. 이 책의 컴퓨터에서 만든 이미지는 `docker images` 기준으로 약 1.6GB였어요.

```bash
# examples/vol3 폴더에서(맥·윈도우·리눅스 같다)
docker build -t python-book-ros:lyrical ros

# 장 폴더를 컨테이너의 /src에 연결하고 그 폴더에서 시작한다
cd 05-ros2-basics
docker run -it --rm -v "$PWD":/src -w /src python-book-ros:lyrical          # 맥·리눅스, 윈도우 PowerShell
docker run -it --rm -v "%cd%":/src -w /src python-book-ros:lyrical          # 윈도우 명령 프롬프트(cmd)

# 같은 컨테이너에 터미널을 하나 더 열 때
docker ps                                       # 이름(NAMES 열) 확인
docker exec -it <컨테이너 이름> bash
```

옵션의 뜻은 5장에서 설명한 그대로입니다. `-v 내_폴더:/src`가 장 폴더를 상자 안의 `/src`로 연결하고, `-w /src`가 그 폴더에서 시작하게 하고, `--rm`은 나올 때 상자를 지워요. 상자를 지워도 `/src`에 쓴 파일은 내 컴퓨터의 장 폴더에 남습니다. 거꾸로 `/src` 밖(예: `/tmp`, `/root`)에 만든 파일은 상자와 함께 사라지니, 남길 결과는 꼭 `/src`에 쓰세요. PowerShell에서는 `$PWD`가 지금 폴더로 바뀌어 맥과 같은 명령이 됩니다.

들어간 뒤에는 환경과 더한 패키지가 제대로 있는지 확인해 봅시다.

<<CODE a04_ros_packages>>

<<OUT a04_ros_packages>>

우분투 26.04, 파이썬 3.14, NumPy 2.3, SciPy 1.16입니다. **호스트의 uv 환경(파이썬 3.12, NumPy 2.5)과 다른 파이썬**이라는 것을 꼭 기억하세요. 그래서 컨테이너 안에는 MuJoCo도 PyTorch도 없고, 컨테이너 밖에는 rclpy가 없습니다. 5·6장의 예제가 이 경계를 어떻게 넘는지가 다음 소제목의 이야기예요. 패키지 판 번호 뒤의 `resolute`는 우분투 26.04의 이름(Resolute)이고, 날짜는 그 패키지가 만들어진 때입니다.

### 장 폴더의 두 종류 파일: 컨테이너용과 _host

5·6장의 장 폴더에는 세 종류의 블록 파일이 있습니다.

| 파일 | 어디서 실행하나 | 예 |
|---|---|---|
| `bNN_이름.py` | 컨테이너 안, `python3 /src/bNN_이름.py` | 노드, tf2 조회 |
| `bNN_이름.sh` | 컨테이너 안, `bash /src/bNN_이름.sh` | `ros2` 명령, launch |
| `bNN_이름_host.py` | **컨테이너 밖**, `uv run python bNN_이름_host.py` | 기록을 읽어 그림 그리기, MuJoCo 렌더 |

이름이 `_host`로 끝나는 파일은 컨테이너가 `/src`에 남긴 파일(CSV, NumPy 배열)을 내 컴퓨터의 uv 환경에서 읽어 matplotlib이나 MuJoCo로 그림을 그립니다. 5장 실습의 궤적 그림, 6장의 tf 그림과 MuJoCo로 URDF를 띄운 그림이 그렇게 만들어졌어요. 컨테이너와 호스트가 같은 장 폴더를 보고 있으니, 파일 하나로 두 환경이 이야기를 나누는 셈입니다.

이 책의 출력을 만들 때는 블록마다 새 컨테이너를 `--network none`으로 띄워 실행했습니다. 같은 컴퓨터에서 여러 예제를 동시에 돌렸기 때문에, 다른 컨테이너의 노드가 DDS 탐색으로 끼어들지 않게 상자마다 네트워크를 끊은 거예요. 상자 하나 안의 노드끼리는 네트워크가 없어도 서로 잘 찾습니다. 여러분이 한 번에 하나씩 실습할 때는 이 옵션이 필요 없어요.

### 패키지를 더 넣고 싶을 때

이 이미지에는 5·6장에 필요한 것만 들어 있습니다. 6장 6.8절의 RViz, 관절 슬라이더 GUI, 14장 끝에서 소개한 Nav2는 들어 있지 않아요. 잠깐 시험해 볼 때는 컨테이너 안에서 `apt-get`으로 설치하면 되지만, `--rm`으로 띄운 상자는 나오면 사라지니 설치도 사라집니다. 오래 쓸 거라면 이 책의 이미지를 바탕으로 내 이미지를 하나 더 만드세요. 이 책의 Dockerfile은 그대로 두고 새 파일을 쓰는 거예요.

```dockerfile
# 내_이미지/Dockerfile: 책의 이미지 위에 Nav2와 RViz를 더한다
FROM python-book-ros:lyrical
RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-lyrical-navigation2 \
        ros-lyrical-nav2-bringup \
        ros-lyrical-rviz2 \
        ros-lyrical-joint-state-publisher-gui \
    && rm -rf /var/lib/apt/lists/*
```

`docker build -t python-book-ros:nav2 내_이미지`로 만들고 `python-book-ros:lyrical` 대신 이 이름으로 띄우면 됩니다. 위 네 패키지는 2026년 10월에 이 이미지 안에서 `apt-cache policy`로 Lyrical용 패키지가 있는 것을 확인했어요. 다만 RViz와 슬라이더 GUI는 **창을 띄우는** 프로그램이라, 화면 없는 컨테이너에서는 설치해도 창이 뜨지 않습니다. 컨테이너에 화면을 연결하는 방법(리눅스의 X11 연결, 원격 데스크톱 등)은 운영체제마다 다르고 손이 많이 가니, RViz를 본격적으로 쓰려면 ROS 2를 직접 설치한 우분투 데스크톱이 가장 편해요.

> **Q. 7장의 서보 키트를 컨테이너에서 쓸 수 있나요?**
> 7장의 직렬 통신 예제는 컨테이너가 아니라 호스트의 uv 환경(`pyserial`)에서 돌아갑니다. ROS 2 노드에서 실물 서보를 다루고 싶다면 리눅스에서는 `docker run --device /dev/ttyACM0 ...`처럼 장치 파일을 상자에 넘겨줄 수 있어요. 맥과 윈도우의 Docker Desktop은 컨테이너가 가상 머신 안에서 돌기 때문에 USB 장치를 넘기는 일이 리눅스처럼 간단하지 않습니다. 실물 키트를 ROS 2로 다룰 계획이라면 우분투 컴퓨터(라즈베리파이나 Jetson 포함, 7장 7.10절)를 쓰는 것이 가장 덜 고생스러워요.

## A.5 ROS_DOMAIN_ID와 여러 컨테이너

5장 5.1절에서 ROS 2의 노드는 DDS로 **같은 네트워크의 노드를 저절로 찾는다**고 했습니다. 편리하지만, 한 교실에서 여러 사람이 실습하거나 내 컴퓨터에서 실험 두 개를 따로 돌릴 때는 서로의 토픽이 섞여요. 이때 쓰는 것이 환경 변수 `ROS_DOMAIN_ID`입니다. 번호가 같은 노드끼리만 서로를 찾아요(정하지 않으면 0). 상자 하나 안에서 받는 쪽은 도메인 1로 두고, 보내는 쪽 번호만 바꿔 보겠습니다.

<<CODE a05_domain>>

<<OUT a05_domain>>

같은 `/chatter` 토픽인데 도메인이 같을 때만 메시지가 건너갔습니다. 도메인 2에서 보낸 메시지는 5초 동안 보냈는데도 도메인 1의 구독자에게 하나도 닿지 않았어요. 토픽 이름을 바꾸지 않고도 통째로 다른 세상이 되는 셈입니다.

컨테이너 여러 개도 마찬가지입니다. 이 책의 컴퓨터에서 아래처럼 두 컨테이너를 따로 띄워 보니, 기본 네트워크에서 서로의 토픽을 주고받았고(받는 쪽에 `data: hello`가 찍힘), 받는 쪽을 `-e ROS_DOMAIN_ID=7`, 보내는 쪽을 `-e ROS_DOMAIN_ID=8`로 띄우자 아무것도 받지 못했어요.

```bash
# 터미널 1: 받는 상자
docker run -it --rm -e ROS_DOMAIN_ID=7 python-book-ros:lyrical \
    ros2 topic echo /chatter std_msgs/msg/String
# 터미널 2: 보내는 상자(번호를 7로 맞추면 받고, 8로 바꾸면 못 받는다)
docker run -it --rm -e ROS_DOMAIN_ID=7 python-book-ros:lyrical \
    ros2 topic pub -r 2 /chatter std_msgs/msg/String "{data: hello}"
```

정리하면 이렇습니다.

- 혼자 실습할 때는 아무것도 정하지 않아도 됩니다(모두 도메인 0).
- 같은 네트워크에서 여러 사람이 실습하면 사람마다 다른 번호를 주세요. ROS 2 문서는 0~101 사이의 번호를 권합니다. 번호마다 DDS가 쓰는 포트가 달라지는데, 큰 번호는 운영체제가 다른 용도로 쓰는 포트와 겹칠 수 있기 때문이에요.
- 실험이 서로 절대 섞이면 안 되면, 이 책의 출력처럼 상자마다 `--network none`으로 아예 네트워크를 끊는 방법도 있습니다. 대신 그 상자는 바깥 누구와도 이야기할 수 없어요.
- 로봇과 노트북처럼 **다른 컴퓨터**의 노드끼리 이야기하게 하려면 둘이 같은 네트워크에 있고 번호가 같아야 합니다. 맥·윈도우의 Docker Desktop 컨테이너는 가상 머신 안의 별도 네트워크에 있어서, 다른 컴퓨터의 노드와 바로 이어지지 않을 수 있어요. 여러 컴퓨터를 잇는 실습은 리눅스 호스트에서 하는 편이 간단합니다.

## A.6 내려받는 모델과 데이터: 위치와 라이선스

### 어디에 쌓일까

9장부터는 사전학습 가중치와 사진을 처음 실행할 때 내려받습니다. 받은 파일이 쌓이는 곳은 세 군데예요.

- **`BOOK_DATA_DIR`**: 이 책의 예제가 직접 받거나 만드는 파일(10장의 사진, 18장의 시연 데이터와 DAgger 정책). 2권 부록 A와 같은 규칙으로, 환경 변수가 있으면 그 폴더, 없으면 지금 폴더의 `data`입니다.
- **torch 캐시**: torchvision 가중치(9장 Faster R-CNN, 10장 Keypoint R-CNN). 기본은 `~/.cache/torch/hub`이고, 환경 변수 `TORCH_HOME`으로 옮길 수 있어요.
- **Hugging Face 캐시**: transformers 모델(19장). 기본은 `~/.cache/huggingface/hub`이고, `HF_HOME`으로 옮깁니다.

이 책의 출력을 만들 때는 장마다 받지 않도록 `BOOK_DATA_DIR`을 `~/.cache/python-book-data`로, `TORCH_HOME`을 그 아래 `torch`로 정해 두었어요. 그 상태에서 얼마나 쌓였는지 재 보겠습니다.

<<CODE a06_paths_host>>

<<OUT a06_paths_host>>

torchvision 가중치 두 개가 합쳐 300MB 남짓이고, 19장의 Hugging Face 모델 네 개가 합쳐 약 5.3GB입니다. 그중 Qwen2.5-1.5B가 3GB 가까이로 가장 커요. 19장 19.5절의 1.5B 비교를 건너뛸 생각이라면 이만큼을 아낄 수 있습니다. 이 책 예제가 만드는 데이터는 18장의 시연 데이터 10MB 정도로 작아요. 디스크가 빠듯하면 위의 환경 변수로 캐시를 외장 디스크로 옮기세요.

```bash
# 맥·리눅스: 셸 설정 파일(~/.zshrc 등)에 넣어 두면 모든 장이 같은 폴더를 쓴다
export BOOK_DATA_DIR=~/book-data
export TORCH_HOME=~/book-data/torch
export HF_HOME=~/book-data/huggingface
# 윈도우 PowerShell(지금 창에서만)
$env:BOOK_DATA_DIR = "$HOME\book-data"
```

### 라이선스 요약

책에 결과를 싣고 여러분이 예제를 내려받아 쓰는 만큼, 본문에서 쓴 모델과 사진의 조건을 장마다 적어 두었습니다. 그 내용을 한 표로 모았어요. 모델 라이선스는 각 장에서 모델 카드와 문서로 확인했고, 이 부록을 쓰며 Hugging Face 모델 카드와 위키미디어 공용의 파일 정보를 다시 조회해 확인했습니다.

| 장 | 무엇 | 출처 | 조건 |
|---|---|---|---|
| 9장 | Faster R-CNN MobileNetV3-Large FPN (`COCO_V1` 가중치) | torchvision | 코드는 BSD. 가중치는 COCO 데이터셋으로 학습했으며, torchvision 문서는 가중치가 학습 데이터에서 비롯된 별도 조건을 가질 수 있으니 용도에 맞는지 확인하라고 안내한다 |
| 10장 | Keypoint R-CNN ResNet50 FPN (`COCO_V1` 가중치) | torchvision | 9장과 같다 |
| 10장 | 미시간 대학 육상 선수 사진(1913년 무렵) | 위키미디어 공용, 원본은 미국 의회도서관(Bain News Service) | 퍼블릭 도메인 |
| 10장 | 고등학교 육상 대회 사진(1912년) | 위키미디어 공용, 원본은 마이애미 대학 도서관 디지털 컬렉션 | 퍼블릭 도메인 |
| 19장 | SmolVLM-500M-Instruct | Hugging Face `HuggingFaceTB/SmolVLM-500M-Instruct` | Apache-2.0 (모델 카드) |
| 19장 | OWLv2 (owlv2-base-patch16-ensemble) | Hugging Face `google/owlv2-base-patch16-ensemble` | Apache-2.0 (모델 카드) |
| 19장 | Qwen2.5-0.5B-Instruct, Qwen2.5-1.5B-Instruct | Hugging Face `Qwen/...` | Apache-2.0 (모델 카드) |
| 1~21장 | MuJoCo 장면, 시연 데이터, 합성 사진 | 이 책의 예제가 직접 만든 것 | 예제 코드와 같은 조건 |

19장 19.6절의 VLA 표(SmolVLA, π0, OpenVLA)는 모델 저장소의 정보만 읽고 가중치는 내려받지 않았습니다. 그 표에 적은 대로 π0의 가중치 카드는 gemma 라이선스처럼 Apache-2.0이 아닌 조건을 달고 있으니, 쓰기 전에 직접 읽어 보세요. 예제 환경의 소프트웨어는 패키지 정보에 적힌 대로 MuJoCo·OpenCV·transformers·anthropic이 Apache-2.0, NumPy·SciPy·pyserial·torchvision이 BSD 계열, Gymnasium이 MIT, matplotlib이 PSF 기반 라이선스이고, PyTorch는 BSD-3-Clause를 비롯한 여러 조건이 함께 적혀 있습니다.

이 표는 이 책의 예제에 대한 정리일 뿐 법률 검토가 아닙니다. 10장에서 말했듯, 모델을 제품에 넣을 때는 코드, 가중치, 학습 데이터의 조건을 모두 직접 읽고, 필요하면 전문가의 확인을 받으세요.

## A.7 Anthropic API 키(19장 선택 절)

19장 19.8절은 Claude에게 지시를 계획하게 하는 선택 절입니다. 이 절만 Anthropic의 API 키가 필요하고, API는 쓴 만큼 요금을 내는 유료 서비스예요. 키가 없어도 다른 모든 장을 따라오는 데는 문제가 없습니다.

키를 다루는 원칙은 하나입니다. **키는 환경 변수에만 두고, 코드에는 절대 적지 않는다.** 코드에 적은 키는 깃 저장소에 올리거나, 화면을 공유하거나, 파일을 동료에게 보내는 순간 새어 나가요. 19장의 코드는 `ANTHROPIC_API_KEY` 환경 변수에서 키를 읽고, 없으면 안내를 찍고 끝납니다. `anthropic` 패키지도 `api_key`를 주지 않으면 같은 환경 변수를 스스로 읽어요(anthropic 2.3.0 소스에서 확인).

```bash
# 맥·리눅스: 지금 터미널에서만
export ANTHROPIC_API_KEY="키를 여기에"
uv run python 19-foundation-models/b15_claude_plan.py

# 윈도우 PowerShell: 지금 창에서만
$env:ANTHROPIC_API_KEY = "키를 여기에"
```

몇 가지를 덧붙이면 이렇습니다.

- 셸 설정 파일에 넣어 두면 편하지만, 그 파일을 dotfiles 저장소 같은 곳에 올리지 않도록 조심하세요. `.env` 파일에 둔다면 그 파일 이름을 `.gitignore`에 꼭 넣습니다.
- 키가 새어 나갔다고 의심되면 Anthropic 콘솔에서 그 키를 바로 지우고 새로 만드세요. 지운 키는 더 이상 쓸 수 없습니다.
- 콘솔에서 사용 한도를 정해 두면, 반복문이 실수로 API를 끝없이 부르는 일이 생겨도 요금이 한도에서 멈춥니다. 19장 코드의 `최대_왕복`(주고받기 상한)과 같은 생각을 계정 쪽에도 걸어 두는 거예요.
- 모델 이름은 19장 코드 맨 위의 상수 `모델_ID` 한 곳에만 있습니다. 새 모델이 나오면 거기만 바꾸세요.

## A.8 자주 만나는 설치 문제

### 컨테이너 안에서 mujoco를 찾지 못할 때

5·6장 컨테이너 안에서 MuJoCo나 PyTorch를 쓰는 블록을 실행하면 이렇게 됩니다.

```text
ModuleNotFoundError: No module named 'mujoco'
```

A.4절에서 본 대로 컨테이너의 파이썬(3.14)과 호스트의 uv 환경(3.12)은 다른 파이썬입니다. MuJoCo로 그림을 그리는 블록은 이름이 `_host`로 끝나고, 컨테이너 밖에서 `uv run python`으로 실행해요. 반대로 호스트에서 `import rclpy`가 안 되는 것도 정상입니다.

### 이미지를 찾지 못할 때

`docker build`를 하기 전에 `docker run`부터 하면 Docker는 같은 이름의 이미지를 인터넷 저장소에서 찾으려다 실패합니다.

```text
Unable to find image 'python-book-ros:missing' locally
docker: Error response from daemon: pull access denied for python-book-ros, repository does not exist or may require 'docker login'
```

`python-book-ros`는 여러분 컴퓨터에서 만드는 이미지라 인터넷에는 없어요. `examples/vol3`에서 `docker build -t python-book-ros:lyrical ros`를 먼저 하세요. 이름 뒤의 태그(`:lyrical`)까지 똑같이 써야 합니다. Docker Desktop이 꺼져 있을 때는 `docker` 명령이 Docker 데몬에 연결할 수 없다는 오류를 내니, Docker Desktop을 먼저 실행하세요.

### 맥에서 뷰어가 뜨지 않을 때

A.3절에서 본 `launch_passive requires that the Python script be run under mjpython on macOS`가 나오면 `uv run mjpython 내코드.py`로 실행하세요. 같은 맥에서 `MUJOCO_GL=egl`처럼 리눅스용 값을 넣으면 `RuntimeError: invalid value for environment variable MUJOCO_GL: egl`로 렌더러를 만들지 못합니다. 리눅스 서버용 설정을 셸 설정 파일에 넣어 둔 채 맥에서 실행했을 때 흔히 만나요. `unset MUJOCO_GL`로 지우면 됩니다.

### 리눅스 서버에서 렌더링이 실패할 때

`FatalError: an OpenGL platform library has not been loaded into this process`는 화면이 없는데 기본값 GLFW로 그리려 했다는 뜻입니다. A.3절대로 `MUJOCO_GL=egl` 또는 `osmesa`를 정하고, 해당 시스템 라이브러리(우분투라면 `libegl1` 또는 `libosmesa6`)를 설치하세요.

### 직렬 포트를 열 수 없을 때

7장에서 실물 키트를 쓸 때 리눅스에서 포트 권한 오류가 나면, 사용자를 포트를 쓸 수 있는 그룹에 넣어야 합니다. 우분투에서는 보통 `dialout` 그룹이고, 넣은 뒤에는 다시 로그인해야 적용돼요. 7장 7.11절에서 말했듯 LeRobot 문서의 안내를 따르세요. 포트 이름은 운영체제마다 다르니(A.2절 표), 키트를 꽂기 전후의 포트 목록을 비교해 찾는 것이 가장 확실합니다.

### 모델 내려받기가 느리거나 디스크가 찰 때

19장 모델 네 개만 5GB가 넘습니다(A.6절). 처음 실행이 오래 걸리는 것은 내려받기 때문이고, 두 번째부터는 캐시에서 바로 읽어요. 디스크가 빠듯하면 `HF_HOME`과 `TORCH_HOME`을 다른 디스크로 옮기고, 다 쓴 모델은 캐시 폴더에서 지우면 됩니다. 지워도 다음에 필요할 때 다시 받아요.
