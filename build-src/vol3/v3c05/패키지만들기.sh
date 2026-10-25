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
