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
