# xacro로 .xacro 파일을 펼쳐 보통 URDF를 만든다
cd "$(dirname "$0")"
xacro 예제팔.urdf.xacro > /tmp/arm6.urdf
wc -l 예제팔.urdf.xacro /tmp/arm6.urdf
echo "--- 펼쳐진 joint3 ---"
grep -A6 '<joint name="joint3"' /tmp/arm6.urdf
echo "--- check_urdf ---"
check_urdf /tmp/arm6.urdf | tail -8
echo "--- 명령줄에서 tool_length:=0.12 ---"
xacro 예제팔.urdf.xacro tool_length:=0.12 | grep -A4 '<joint name="tip_joint"'
