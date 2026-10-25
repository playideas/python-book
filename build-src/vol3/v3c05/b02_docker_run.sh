# 저장소의 examples/vol3 폴더에서 한다(맥·윈도우·리눅스 모두 같다)
docker build -t python-book-ros:lyrical ros       # 이미지 만들기. 처음 한 번만, 몇 분 걸린다
cd 05-ros2-basics
# 이 장 폴더를 컨테이너의 /src에 연결하고, /src에서 시작하는 셸로 들어간다
docker run -it --rm -v "$PWD":/src -w /src python-book-ros:lyrical
