# Chapter 6. URDF와 시각화: 로봇의 몸을 파일로 적기

> **학습 목표**  
> - URDF가 링크와 관절로 로봇의 몸을 나무 모양으로 적는 방식이라는 것을 알고, 작은 팔의 URDF를 읽고 쓰기
> - 관절 `origin`의 `rpy`가 2장의 고정 축 롤·피치·요(`Rz @ Ry @ Rx`)라는 것을 실행으로 확인하기
> - 링크의 세 얼굴(visual, collision, inertial)을 나누는 이유와, 질량·관성이 시뮬레이션을 어떻게 바꾸는지 보기
> - 3장의 예제 6자유도 팔을 URDF로 옮기고, 직접 짠 순기구학과 tf2가 같은 손끝 위치를 내는지 검산하기
> - xacro의 속성·매크로·인자로 반복을 줄이기
> - robot_state_publisher와 joint_state_publisher가 관절 각도를 tf2 좌표계 나무로 바꾸는 구조를 이해하고, tf2의 (target, source) 순서를 이 책의 `T_A_B` 이름과 맞추기
> - RViz와 MuJoCo로 URDF를 눈으로 확인하고, 3관절 팔의 손끝 궤적을 tf로 기록해 그림으로 그리기

---

## 들어가며: 같은 팔을 세 번째로 적습니다

3장에서 예제 6자유도 팔을 처음 만났을 때, 우리는 그 팔을 파이썬 목록으로 적었습니다. `("허리", [0, 0, 0.10], [0, 0, 1])`처럼 관절마다 "앞 관절 기준 위치와 회전축"을 적은 여섯 줄이었죠. 3.9절에서는 같은 팔을 MuJoCo의 장면 파일(MJCF)로 옮겨 검산했고, 4장에서는 MJCF로 탁자와 상자까지 갖춘 장면을 만들었습니다.

그런데 한 가지 문제가 있습니다. 파이썬 목록은 우리 코드만 알아듣고, MJCF는 MuJoCo만 알아들어요. 진짜 로봇 소프트웨어는 여러 프로그램이 함께 돕니다. 5장에서 본 것처럼 ROS 2에서는 팔을 움직이는 노드, 카메라를 읽는 노드, 화면에 로봇을 그리는 노드, 경로를 계획하는 노드가 따로 돌아요. 이 노드들이 모두 "이 로봇은 어떻게 생겼나"를 알아야 하는데, 각자 다른 형식으로 적어 두면 금방 서로 어긋납니다. 이사할 때 가구 배치도를 한 장 그려서 모두에게 나눠 주는 것처럼, 로봇의 몸도 **모두가 읽는 한 장의 설계도**가 필요합니다.

ROS 세계에서 그 설계도가 **URDF(Unified Robot Description Format)** 입니다. XML로 된 글 파일이고, 생김새는 MJCF와 비슷해요. 3장 예제 팔의 첫 관절 하나만 URDF로 적고, ROS 2와 함께 설치되는 파이썬 라이브러리 `urdf_parser_py`로 읽어 보겠습니다.

```python
from urdf_parser_py.urdf import URDF

# 링크 둘과 그 둘을 잇는 회전 관절 하나: 3장 예제 팔의 첫 관절(허리)만 떼어 낸 것
글 = """
<robot name="waist_only">
  <link name="base_link"/>
  <link name="link1"/>
  <joint name="joint1" type="revolute">
    <parent link="base_link"/>
    <child link="link1"/>
    <origin xyz="0 0 0.1" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.14" upper="3.14" effort="10" velocity="2"/>
  </joint>
</robot>
"""
로봇 = URDF.from_xml_string(글)
관절 = 로봇.joints[0]
print("로봇 이름:", 로봇.name)
print("링크:", [링크.name for 링크 in 로봇.links])
print(f"관절 {관절.name}: {관절.type}, {관절.parent} → {관절.child}")
print("  고정 위치 xyz:", 관절.origin.xyz, "/ 회전축:", 관절.axis)
print("3장의 같은 관절: ('허리', [0, 0, 0.10], [0, 0, 1])")
```

```text
로봇 이름: waist_only
링크: ['base_link', 'link1']
관절 joint1: revolute, base_link → link1
  고정 위치 xyz: [0.0, 0.0, 0.1] / 회전축: [0.0, 0.0, 1.0]
3장의 같은 관절: ('허리', [0, 0, 0.10], [0, 0, 1])
```

링크(`link`) 두 개와 그 둘을 잇는 관절(`joint`) 하나입니다. 관절의 `origin xyz`가 3장의 "고정 위치", `axis`가 "회전축"이에요. 숫자가 3장 목록의 한 줄과 똑같죠? 3장에서 "URDF와 MuJoCo도 관절을 부모 기준 위치와 축으로 적는다"고 미리 말해 둔 게 바로 이것입니다.

이 장에서는 작은 2관절 팔로 URDF 문법을 익히고, `rpy`가 2장의 어떤 회전인지 확인한 뒤, 3장의 6자유도 팔을 URDF로 옮깁니다. 반복은 **xacro**로 줄이고, ROS 2의 `robot_state_publisher`가 관절 각도를 **tf2 좌표계 나무**로 바꾸는 과정을 직접 띄워 3장의 순기구학과 검산해요. 마지막에는 3관절 팔로 손끝 궤적을 기록해 그림으로 그립니다.

> **Q. 이 장의 예제는 어디서 실행하나요?**
> ROS 2가 필요한 예제는 5장 5.1절에서 띄운 Docker 이미지 안에서 실행합니다. ROS 2 Lyrical(파이썬 3.14)에 `robot_state_publisher`, `joint_state_publisher`, tf2, xacro, `urdf_parser_py`가 들어 있어요. 그림을 그리는 예제와 MuJoCo 예제는 1~4장처럼 내 컴퓨터의 `uv` 환경에서 실행하고, 컨테이너가 남긴 파일을 읽어 그립니다. 예제 폴더의 파일 이름이 `_host`로 끝나면 내 컴퓨터에서, 아니면 컨테이너에서 실행하는 블록이에요.

## 6.1 URDF의 뼈대: 링크와 관절

### 뼈와 마디를 글로

3장 3.1절에서 로봇 팔을 뼈(링크)와 마디(관절)로 나눠 봤죠. URDF는 이 구분을 그대로 글로 옮깁니다. 규칙은 몇 개 안 돼요.

1. `<robot>` 안에 `<link>`와 `<joint>`를 늘어놓는다. 순서는 상관없다
2. `<joint>`는 부모 링크(`parent`) 하나와 자식 링크(`child`) 하나를 잇는다
3. 링크마다 부모는 **많아야 하나**다. 부모가 없는 링크는 딱 하나여야 하고, 그것이 **뿌리(root)** 다
4. 자식 링크의 좌표계는 부모 링크 좌표계에서 `origin`만큼 옮기고 돌린 곳에 있다. 관절이 움직이면 그 위에서 `axis`를 따라 더 움직인다

3번 규칙 때문에 URDF로 적은 로봇은 늘 **나무(tree)** 모양입니다. 줄기에서 가지가 갈라질 수는 있지만(두 팔 로봇), 가지가 다시 만나는 고리는 만들 수 없어요. 4번이 바로 3장의 `이동(위치) @ 축_회전(축, 각)`입니다.

3장 3.2절의 2링크 팔(위팔 0.4m, 아래팔 0.3m)을 URDF로 적어 보겠습니다. 다음 내용을 `두관절팔.urdf`로 저장하세요.

```xml
<?xml version="1.0"?>
<!-- 3장 3.2절의 2링크 팔(위팔 0.4m, 아래팔 0.3m)을 URDF로 적은 것 -->
<robot name="two_link_arm">
  <link name="base_link">
    <visual>
      <origin xyz="0 0 0.025"/>
      <geometry><cylinder radius="0.06" length="0.05"/></geometry>
    </visual>
  </link>

  <joint name="shoulder" type="revolute">
    <parent link="base_link"/>
    <child link="upper_arm"/>
    <origin xyz="0 0 0.05" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.1416" upper="3.1416" effort="5.0" velocity="2.0"/>
  </joint>

  <link name="upper_arm">
    <visual>
      <origin xyz="0.2 0 0" rpy="0 1.5708 0"/>
      <geometry><cylinder radius="0.02" length="0.4"/></geometry>
    </visual>
    <collision>
      <origin xyz="0.2 0 0" rpy="0 1.5708 0"/>
      <geometry><cylinder radius="0.025" length="0.4"/></geometry>
    </collision>
    <inertial>
      <origin xyz="0.2 0 0"/>
      <mass value="0.5"/>
      <inertia ixx="0.0001" ixy="0" ixz="0" iyy="0.00672" iyz="0" izz="0.00672"/>
    </inertial>
  </link>

  <joint name="elbow" type="revolute">
    <parent link="upper_arm"/>
    <child link="forearm"/>
    <origin xyz="0.4 0 0" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-2.618" upper="2.618" effort="3.0" velocity="2.0"/>
  </joint>

  <link name="forearm">
    <visual>
      <origin xyz="0.15 0 0" rpy="0 1.5708 0"/>
      <geometry><cylinder radius="0.02" length="0.3"/></geometry>
    </visual>
    <collision>
      <origin xyz="0.15 0 0" rpy="0 1.5708 0"/>
      <geometry><cylinder radius="0.025" length="0.3"/></geometry>
    </collision>
    <inertial>
      <origin xyz="0.15 0 0"/>
      <mass value="0.3"/>
      <inertia ixx="0.00006" ixy="0" ixz="0" iyy="0.00228" iyz="0" izz="0.00228"/>
    </inertial>
  </link>

  <joint name="tip_joint" type="fixed">
    <parent link="forearm"/>
    <child link="tip"/>
    <origin xyz="0.3 0 0"/>
  </joint>

  <link name="tip"/>
</robot>
```

처음 보면 길지만, 덩어리로 보면 단순합니다. 링크 네 개(`base_link`, `upper_arm`, `forearm`, `tip`)와 관절 세 개(`shoulder`, `elbow`, `tip_joint`)예요. 관절마다 읽어 볼게요.

- **shoulder**: 바닥(`base_link`)에서 0.05m 위에 있고, z축을 중심으로 도는 회전 관절(`revolute`)입니다. 3장의 2링크 팔처럼 위에서 내려다본 평면 안에서 돌아요. `limit`에는 돌 수 있는 범위(rad)와 낼 수 있는 힘(`effort`, N·m), 최고 속도(`velocity`, rad/s)를 적습니다
- **elbow**: 위팔 좌표계에서 x축으로 0.4m 나간 곳, 곧 위팔 끝에 있습니다. 범위는 ±2.618rad(±150도)로 좁혔어요
- **tip_joint**: 아래팔 끝 0.3m에 손끝 좌표계를 하나 붙이는 **고정 관절(`fixed`)** 입니다. 움직이지 않는 관절이 왜 필요할까요? "손끝은 어디냐"고 물을 이름이 필요하기 때문이에요. 3장 3.9절의 MJCF에서 손끝에 `site`를 둔 것과 같은 역할입니다

링크 쪽의 `visual`, `collision`, `inertial`은 6.3절에서 자세히 보고, 지금은 "보이는 모양, 부딪히는 모양, 질량"이라고만 알아 두세요.

ROS에는 URDF를 검사하는 `check_urdf` 명령이 있습니다. 문법이 맞는지, 링크들이 나무 모양으로 이어지는지 확인해 줘요.

```bash
# 이 스크립트가 있는 폴더의 URDF를 검사한다: 문법, 부모·자식 연결, 뿌리 링크
cd "$(dirname "$0")"
check_urdf 두관절팔.urdf
```

```text
robot name is: two_link_arm
---------- Successfully Parsed XML ---------------
root Link: base_link has 1 child(ren)
    child(1):  upper_arm
        child(1):  forearm
            child(1):  tip
```

뿌리가 `base_link`이고, 거기서 `upper_arm`, `forearm`, `tip`이 한 줄로 이어집니다. 가지가 없는 사슬이죠. 파이썬에서도 같은 정보를 꺼내 볼 수 있습니다.

```python
from pathlib import Path

import numpy as np
from urdf_parser_py.urdf import URDF

로봇 = URDF.from_xml_file(str(Path(__file__).with_name("두관절팔.urdf")))
print("뿌리 링크:", 로봇.get_root())
print("바닥 → 손끝 사슬:", 로봇.get_chain(로봇.get_root(), "tip"))

for 링크 in 로봇.links:
    가진것 = [이름 for 이름, 값 in [("visual", 링크.visual), ("collision", 링크.collision),
                                ("inertial", 링크.inertial)] if 값 is not None]
    질량 = f", 질량 {링크.inertial.mass}kg" if 링크.inertial else ""
    print(f"링크 {링크.name:9s}: {', '.join(가진것) or '(빈 링크)'}{질량}")

for 관절 in 로봇.joints:
    줄 = f"관절 {관절.name:9s}: {관절.type:8s} 위치 {관절.origin.xyz}"
    if 관절.limit and 관절.type != "fixed":
        범위 = np.round(np.rad2deg([관절.limit.lower, 관절.limit.upper]), 1)
        줄 += f", 축 {관절.axis}, 범위 {범위[0]}~{범위[1]}도"
    print(줄)
```

```text
뿌리 링크: base_link
바닥 → 손끝 사슬: ['base_link', 'shoulder', 'upper_arm', 'elbow', 'forearm', 'tip_joint', 'tip']
링크 base_link: visual
링크 upper_arm: visual, collision, inertial, 질량 0.5kg
링크 forearm  : visual, collision, inertial, 질량 0.3kg
링크 tip      : (빈 링크)
관절 shoulder : revolute 위치 [0.0, 0.0, 0.05], 축 [0.0, 0.0, 1.0], 범위 -180.0~180.0도
관절 elbow    : revolute 위치 [0.4, 0.0, 0.0], 축 [0.0, 0.0, 1.0], 범위 -150.0~150.0도
관절 tip_joint: fixed    위치 [0.3, 0.0, 0.0]
```

`get_chain`은 두 링크 사이를 링크와 관절을 번갈아 가며 알려 줍니다. 3장의 순기구학이 반복문으로 따라가던 바로 그 길이에요. `base_link`는 보이는 모양만 있고, `tip`은 아무것도 없는 **빈 링크**입니다. 좌표계 하나를 붙여 두려고 만든 링크니까요. 범위는 rad로 적혀 있으니 사람이 읽을 때만 도로 바꿨습니다.

### 관절의 종류

URDF의 관절은 몇 가지 종류(`type`)가 있습니다. 로봇 팔에서 쓰는 것은 대부분 이 넷이에요.

| type | 움직임 | 관절 값의 단위 | limit | 예 |
|---|---|---|---|---|
| `revolute` | 축을 중심으로 회전, 범위 있음 | rad | 필수(범위, 힘, 속도) | 팔꿈치, 어깨 |
| `continuous` | 축을 중심으로 끝없이 회전 | rad | 힘, 속도만 | 바퀴, 무한 회전 손목 |
| `prismatic` | 축을 따라 직선 이동 | m | 필수 | 승강대, 직선 레일 |
| `fixed` | 움직이지 않음 | 없음 | 없음 | 손끝 표시, 나사로 고정한 카메라 |

`floating`(공중에 뜬 6자유도)과 `planar`(평면 3자유도)도 있지만, 로봇 팔 URDF에서는 거의 볼 일이 없습니다. `axis`를 적지 않으면 기본값은 x축 (1, 0, 0)이에요. 회전축을 z로 생각하고 `axis`를 빼먹으면 엉뚱한 축으로 도는 팔이 되니, 회전·직선 관절에는 늘 `axis`를 적는 습관을 들이세요.

### 흔한 실수와 두 검사기

URDF는 손으로 쓰는 글이라 실수가 잦습니다. 흔한 실수 세 가지를 `check_urdf`와 `urdf_parser_py`에 각각 넣어 보겠습니다.

```python
import subprocess
import tempfile
from pathlib import Path

from urdf_parser_py.urdf import URDF

링크둘 = '<link name="a"/><link name="b"/>'
실수들 = {
    "회전 관절에 limit 없음": f'<joint name="j" type="revolute"><parent link="a"/><child link="b"/>'
                         f'<axis xyz="0 0 1"/></joint>',
    "없는 링크 이름(오타)": '<joint name="j" type="fixed"><parent link="a"/><child link="bb"/></joint>',
    "어디에도 안 이어진 링크": '<link name="c"/><joint name="j" type="fixed"><parent link="a"/><child link="b"/></joint>',
}
with tempfile.TemporaryDirectory() as 폴더:
    for 설명, 본문 in 실수들.items():
        파일 = Path(폴더) / "test.urdf"
        파일.write_text(f'<robot name="r">{링크둘}{본문}</robot>')
        결과 = subprocess.run(["check_urdf", str(파일)], capture_output=True, text=True)
        첫_오류 = next(줄 for 줄 in (결과.stdout + 결과.stderr).splitlines() if 줄.startswith("Error"))
        try:
            뿌리 = URDF.from_xml_file(str(파일)).get_root()   # 읽기만 하면 통과, 뿌리를 찾을 때 걸린다
            파이썬 = f"통과(뿌리 {뿌리})"
        except AssertionError as 오류:
            파이썬 = f"거부({오류})"
        print(f"[{설명}]\n  check_urdf     : {첫_오류.removeprefix('Error:').strip()}\n  urdf_parser_py : {파이썬}")
```

```text
[회전 관절에 limit 없음]
  check_urdf     : Joint [j] is of type REVOLUTE but it does not specify limits
  urdf_parser_py : 통과(뿌리 a)
[없는 링크 이름(오타)]
  check_urdf     : Failed to build tree: child link [bb] of joint [j] not found
  urdf_parser_py : 거부(Multiple roots detected, invalid URDF.)
[어디에도 안 이어진 링크]
  check_urdf     : Failed to find root link: Two root links found: [a] and [c]
  urdf_parser_py : 거부(Multiple roots detected, invalid URDF.)
```

`check_urdf`는 셋 다 정확한 이유와 함께 거부했습니다. 회전 관절에 `limit`이 없다, `bb`라는 링크가 없다, 뿌리가 둘이다. 반면 `urdf_parser_py`는 `limit` 없는 회전 관절을 그냥 통과시켰고, 나머지 둘도 읽기는 했다가 뿌리를 찾는 순간에야 "뿌리가 여럿"이라는 덜 친절한 말로 멈췄어요. 링크 이름 오타가 "뿌리가 여럿"으로 보이는 건, 이어지지 못한 `b`가 부모 없는 링크로 남기 때문입니다.

`robot_state_publisher` 같은 ROS의 C++ 도구들은 `check_urdf`와 같은 엄격한 해석기(urdfdom)를 씁니다. 그러니 **URDF를 고쳤으면 `check_urdf`부터** 돌려 보세요. 파이썬에서 읽힌다고 해서 ROS 도구에서도 읽힌다는 보장은 없습니다.

## 6.2 origin의 rpy는 어떤 회전일까

`두관절팔.urdf`의 원기둥 모양에 `rpy="0 1.5708 0"`이라는 숫자가 붙어 있었죠. URDF는 자세를 **rpy**, 곧 롤·피치·요 세 각도(rad)로 적습니다. 2장 2.4절에서 "롤·피치·요라는 말만으로는 자세가 하나로 정해지지 않는다, 순서와 축 약속을 확인하라"고 했어요. URDF의 약속을 직접 확인해 보겠습니다.

방법은 이렇습니다. 고정 관절 하나에 `rpy`만 적은 URDF를 만들어 `robot_state_publisher`(6.6절에서 자세히 봅니다)에게 주고, tf2에게 그 관절이 만든 회전을 물어 2장의 후보들과 비교해요. 같은 세 숫자를 tf2의 명령줄 도구 `static_transform_publisher`에도 넣어 봅니다. 아래 코드가 쓰는 `tf도구.py`는 6.6절에서 보여 드릴 테니, 지금은 "노드를 띄우고 tf2에 묻는 도구"라고만 생각하세요.

```python
import subprocess

import numpy as np
from scipy.spatial.transform import Rotation

from tf도구 import 상태_발행기, 연결

롤, 피치, 요 = np.deg2rad([10, 20, 30])      # 2장 2.4절과 같은 값
# 고정 관절 하나에 origin rpy만 적은 URDF
urdf = f"""<robot name="rpy_test">
  <link name="base_link"/><link name="tip"/>
  <joint name="j" type="fixed"><parent link="base_link"/><child link="tip"/>
    <origin xyz="0 0 0" rpy="{롤} {피치} {요}"/></joint>
</robot>"""
# 같은 세 숫자를 명령줄 도구 static_transform_publisher에도 준다
정적_발행 = subprocess.Popen(
    ["ros2", "run", "tf2_ros", "static_transform_publisher", "--roll", str(롤), "--pitch", str(피치),
     "--yaw", str(요), "--frame-id", "base_link", "--child-frame-id", "camera"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
with 상태_발행기(urdf), 연결() as 팔:
    R_urdf = 팔.변환("base_link", "tip")[:3, :3]
    R_명령줄 = 팔.변환("base_link", "camera")[:3, :3]
정적_발행.terminate()
정적_발행.wait()

후보 = {"Rz(요) @ Ry(피치) @ Rx(롤)": Rotation.from_euler("z", 요).as_matrix()
        @ Rotation.from_euler("y", 피치).as_matrix() @ Rotation.from_euler("x", 롤).as_matrix(),
        "scipy 소문자 'xyz'(고정 축)": Rotation.from_euler("xyz", [롤, 피치, 요]).as_matrix(),
        "scipy 대문자 'XYZ'(움직이는 축)": Rotation.from_euler("XYZ", [롤, 피치, 요]).as_matrix()}
for 이름, R in 후보.items():
    print(f"{이름:24s}: URDF {np.allclose(R_urdf, R)!s:5s} / static_transform_publisher {np.allclose(R_명령줄, R)}")
```

```text
Rz(요) @ Ry(피치) @ Rx(롤)  : URDF True  / static_transform_publisher True
scipy 소문자 'xyz'(고정 축)   : URDF True  / static_transform_publisher True
scipy 대문자 'XYZ'(움직이는 축) : URDF False / static_transform_publisher False
```

URDF의 `rpy`와 `static_transform_publisher`의 `--roll --pitch --yaw`는 둘 다 `Rz(요) @ Ry(피치) @ Rx(롤)`, 곧 SciPy의 소문자 `"xyz"`(고정 축 롤 → 피치 → 요)입니다. 2장 2.4절에서 "ROS와 URDF의 rpy도 이 약속"이라고 했던 것을 이제 실행으로 확인했어요. 대문자 `"XYZ"`는 아니었습니다. 2장 2.9절에서 MuJoCo의 `euler` 속성은 대문자 `"XYZ"`였으니, **같은 세 숫자라도 URDF의 rpy와 MuJoCo의 euler는 다른 자세**입니다. URDF를 MJCF로 손으로 옮길 때 가장 조심할 곳이에요.

이 약속으로 `두관절팔.urdf`의 `rpy="0 1.5708 0"`을 읽어 볼까요? 롤과 요가 0이니 `Ry(90도)`입니다. 2장 2.3절에서 y축으로 90도 돌리면 앞(x)이 아래(-z)로 간다고 했는데, 거꾸로 보면 z축이 x축 자리로 갑니다(`Ry(90) @ [0, 0, 1] = [1, 0, 0]`). URDF의 원기둥은 늘 자기 z축 방향으로 서 있기 때문에, x축 방향으로 뻗은 위팔 모양을 만들려고 원기둥을 눕힌 거예요. `origin xyz="0.2 0 0"`은 길이 0.4m 원기둥의 가운데를 위팔 한가운데에 두려는 것이고요.

## 6.3 링크의 세 얼굴: visual, collision, inertial

### 왜 셋으로 나눌까

링크 하나에 모양을 두 번(`visual`, `collision`) 적고 질량(`inertial`)까지 따로 적는 게 번거로워 보일 수 있습니다. 셋은 쓰는 사람이 다릅니다.

| 부분 | 무엇 | 누가 쓰나 | 보통의 모양 |
|---|---|---|---|
| `visual` | 사람 눈에 보이는 모양 | RViz 같은 화면 도구 | 자세한 3D 메시(STL, DAE 파일) |
| `collision` | 부딪힘을 계산하는 모양 | 시뮬레이터, 충돌 검사, 경로 계획 | 원기둥·상자·공 같은 단순한 모양, 조금 크게 |
| `inertial` | 질량, 무게중심, 관성 | 시뮬레이터, 동역학 계산 | 숫자 |

보이는 모양은 자세할수록 좋지만, 충돌 계산은 1초에 수백 번 해야 해서 단순할수록 좋습니다. 그래서 `collision`은 단순한 모양으로, 안전을 위해 실제보다 **조금 크게** 잡는 일이 흔합니다. `두관절팔.urdf`에서도 보이는 원기둥은 반지름 0.02m, 부딪히는 원기둥은 0.025m로 적었어요.

### 관성 숫자는 어디서 오나

`inertial`의 `inertia`는 링크를 **돌리기 어려운 정도**를 축별로 적은 3×3 행렬(관성 텐서)의 여섯 칸입니다. 대칭 행렬이라 아홉 칸 중 여섯 칸만 적어요. 4장 4.2절에서 MuJoCo가 모양에서 질량과 관성을 계산해 준다고 했는데, URDF는 이 숫자를 직접 적어야 합니다. 실제 로봇이라면 CAD 프로그램이 계산해 주고, 단순한 모양이라면 공식으로 구할 수 있어요. 꽉 찬 원기둥(질량 m, 반지름 r, 길이 L)이라면 길이 방향 축은 m·r²/2, 그에 수직인 두 축은 m·(3r² + L²)/12입니다.

```python
from pathlib import Path

from urdf_parser_py.urdf import URDF

로봇 = URDF.from_xml_file(str(Path(__file__).with_name("두관절팔.urdf")))


def 원기둥_관성(질량: float, 반지름: float, 길이: float) -> tuple[float, float]:
    """꽉 찬 원기둥의 무게중심 기준 관성: (길이 방향 축, 그에 수직인 축)."""
    return 질량 * 반지름**2 / 2, 질량 * (3 * 반지름**2 + 길이**2) / 12


for 이름 in ["upper_arm", "forearm"]:
    링크 = 로봇.link_map[이름]
    모양 = 링크.collision.geometry                     # 부딪히는 모양(원기둥)의 치수
    관성 = 링크.inertial.inertia
    길이축, 옆축 = 원기둥_관성(링크.inertial.mass, 0.02, 모양.length)   # 막대 반지름 0.02m
    print(f"{이름}: 질량 {링크.inertial.mass}kg, 무게중심 {링크.inertial.origin.xyz}")
    print(f"  공식  ixx {길이축:.5f}, iyy=izz {옆축:.5f}")
    print(f"  URDF  ixx {관성.ixx:.5f}, iyy=izz {관성.iyy:.5f}")
```

```text
upper_arm: 질량 0.5kg, 무게중심 [0.2, 0.0, 0.0]
  공식  ixx 0.00010, iyy=izz 0.00672
  URDF  ixx 0.00010, iyy=izz 0.00672
forearm: 질량 0.3kg, 무게중심 [0.15, 0.0, 0.0]
  공식  ixx 0.00006, iyy=izz 0.00228
  URDF  ixx 0.00006, iyy=izz 0.00228
```

URDF에 적은 숫자가 공식과 맞습니다. 위팔은 x축 방향으로 누운 막대라서 x축(길이 방향)으로 돌리기는 아주 쉽고(0.0001), y나 z축으로 휘두르기는 67배쯤 어렵습니다(0.00672). 막대를 손가락으로 비비며 돌리기는 쉬워도 야구 방망이처럼 휘두르기는 힘든 것과 같아요. 관성은 무게중심 기준이라서, `inertial`의 `origin`에 무게중심(막대 한가운데 0.2m)을 함께 적었습니다.

### MuJoCo로 URDF 읽기

URDF의 `inertial`이 실제로 어떤 일을 하는지는 시뮬레이터에 넣어 봐야 압니다. 반가운 소식은 4장의 MuJoCo가 **URDF를 바로 읽는다**는 거예요. MJCF 글 대신 URDF 글을 넣기만 하면 됩니다.

```python
from pathlib import Path

import mujoco

글 = Path(__file__).with_name("두관절팔.urdf").read_text()
모델 = mujoco.MjModel.from_xml_string(글)               # MuJoCo는 URDF도 바로 읽는다
print("몸체:", [모델.body(i).name for i in range(모델.nbody)])
print("관절:", [모델.joint(i).name for i in range(모델.njnt)], "/ 범위(rad):", 모델.jnt_range[1].round(3))
print("모양(geom) 수:", 모델.ngeom, "/ 질량(kg):", 모델.body_mass.round(3))

# visual을 버리지 말고, 고정된 몸체도 합치지 말라고 MuJoCo 전용 설정을 끼워 넣으면
설정 = '<robot name="two_link_arm">\n  <mujoco><compiler discardvisual="false" fusestatic="false"/></mujoco>'
모델2 = mujoco.MjModel.from_xml_string(글.replace('<robot name="two_link_arm">', 설정))
print("설정 뒤 몸체:", [모델2.body(i).name for i in range(모델2.nbody)], "/ 모양 수:", 모델2.ngeom)

# 위팔의 inertial을 빠뜨리면?
빠뜨림 = 글.split("<inertial>", 1)[0] + 글.split("</inertial>", 1)[1]
모델3 = mujoco.MjModel.from_xml_string(빠뜨림)
위팔 = 모델3.body("upper_arm")
print(f"위팔 inertial 없음 → 질량 {위팔.mass[0]:.3f}kg, 관성 {위팔.inertia.round(5)}")
```

```text
몸체: ['world', 'upper_arm', 'forearm']
관절: ['shoulder', 'elbow'] / 범위(rad): [-2.618  2.618]
모양(geom) 수: 2 / 질량(kg): [0.  0.5 0.3]
설정 뒤 몸체: ['world', 'base_link', 'upper_arm', 'forearm', 'tip'] / 모양 수: 5
위팔 inertial 없음 → 질량 0.785kg, 관성 [0.01059 0.01059 0.00025]
```

읽히기는 했는데, 결과를 보면 MuJoCo가 URDF를 자기 방식대로 고쳐 읽었다는 걸 알 수 있습니다.

- **움직이지 않는 몸체는 합쳐집니다.** `base_link`는 바닥(`world`)에 붙어 있고 `tip`은 아래팔에 고정되어 있으니, MuJoCo는 둘을 따로 두지 않고 부모 몸체에 합쳐 버렸어요. 그래서 몸체가 셋뿐입니다
- **보이는 모양(visual)은 버립니다.** 모양이 두 개뿐인 건 위팔과 아래팔의 `collision`만 남았기 때문이에요. `base_link`에는 `visual`만 있었으니 아무것도 남지 않았습니다
- **관절 범위와 질량은 그대로** 옮겨졌습니다

URDF 안에 `<mujoco>` 요소로 MuJoCo 전용 설정을 끼워 넣으면 이 동작을 바꿀 수 있어요. `discardvisual="false"`로 보이는 모양을 살리고 `fusestatic="false"`로 몸체를 합치지 않게 하니, 몸체 다섯 개와 모양 다섯 개(보이는 것 셋, 부딪히는 것 둘)가 됐습니다. 다른 ROS 도구들은 이 요소를 무시합니다.

마지막 줄은 더 중요합니다. 위팔의 `inertial`을 빠뜨렸더니 오류 없이 질량 0.785kg짜리 위팔이 생겼어요. 우리가 적은 0.5kg이 아닙니다. MuJoCo가 `collision` 원기둥(반지름 0.025m, 길이 0.4m)에 **물의 밀도**를 채워 질량을 지어낸 거예요. π × 0.025² × 0.4 × 1000 = 0.785kg입니다. 4장 4.2절에서 본 "질량을 안 적으면 물의 밀도"가 여기서도 조용히 적용됐어요. 오류가 나지 않으니 모르고 지나가기 쉽습니다.

### 질량이 틀리면 움직임이 틀린다

`inertial`이 틀리면 얼마나 달라질까요? 보이는 모양은 똑같고 `inertial`만 다른 팔 세 개를 만들어, 어깨에 똑같이 0.2N·m의 힘을 1초 동안 줘 보겠습니다. 팔꿈치는 힘을 주지 않아서 자유롭게 휘둘립니다.

```python
from pathlib import Path

import mujoco
import numpy as np

글 = Path(__file__).with_name("두관절팔.urdf").read_text()
경우들 = {
    "올바른 URDF": 글,
    "무게중심 origin을 빠뜨림": 글.replace('<origin xyz="0.2 0 0"/>\n      <mass', '<mass'),
    "질량을 g 단위로 적음": 글.replace('<mass value="0.5"/>', '<mass value="500"/>'),
}
for 이름, 내용 in 경우들.items():
    모델 = mujoco.MjModel.from_xml_string(내용)
    데이터 = mujoco.MjData(모델)
    데이터.qfrc_applied[0] = 0.2                        # 어깨에 0.2N·m 토크를 1초 동안
    while 데이터.time < 1.0:
        mujoco.mj_step(모델, 데이터)
    어깨, 팔꿈치 = np.rad2deg(데이터.qpos)
    print(f"{이름:14s}: 1초 뒤 어깨 {어깨:7.1f}도, 팔꿈치 {팔꿈치:6.1f}도")
```

```text
올바른 URDF      : 1초 뒤 어깨    97.7도, 팔꿈치 -131.3도
무게중심 origin을 빠뜨림: 1초 뒤 어깨   135.6도, 팔꿈치  -84.6도
질량을 g 단위로 적음  : 1초 뒤 어깨     0.3도, 팔꿈치   -0.9도
```

올바른 URDF에서는 1초 뒤 어깨가 97.7도까지 돌았고, 팔꿈치는 반대쪽으로 -131.3도 휘둘렸습니다. 무게중심의 `origin`을 빠뜨린 팔은 무게중심이 어깨 축 위에 있는 것으로 계산되니 훨씬 돌리기 쉬워져서 135.6도까지 돌았어요. 질량을 g 단위로 착각해 500을 적은 팔은 1000배 무거우니 0.3도밖에 못 움직였습니다.

화면에 그리면 세 팔은 모양이 똑같습니다. 그래서 `inertial`의 실수는 시뮬레이션에서 "모터가 생각보다 약하다", "팔이 이상하게 휘청인다"는 모습으로만 드러나요. 17장에서 배울 강화 학습이나 20장의 sim2real에서 시뮬레이션으로 배운 것을 실물로 옮길 때, 이런 숫자 하나가 성패를 가르기도 해요.

## 6.4 3장의 예제 팔을 URDF로

### 목록에서 URDF 글로

이제 3장의 예제 6자유도 팔을 URDF로 옮기겠습니다. 3장 3.9절에서 `예제_팔` 목록을 MJCF 글로 바꾼 `팔모델.py`를 만들었죠. 같은 방법으로 URDF 글을 만드는 `팔URDF.py`를 짭니다. 3장의 `팔도구.py`와 2장의 `회전도구.py`를 이 장의 폴더로 복사해서 함께 씁니다.

링크 이름은 `base_link`, `link1`~`link6`, `tip`, 관절 이름은 `joint1`~`joint6`으로 3장 3.9절의 MJCF와 맞췄습니다. ROS의 좌표계 이름은 영문 소문자와 밑줄로 짓는 것이 관례예요. 관절 i는 `link(i-1)`과 `link(i)`를 잇고, 각 링크는 다음 관절까지 뻗은 막대입니다. 질량은 예제용으로 "1m에 2kg"으로 정하고 6.3절의 원기둥 공식으로 관성을 계산했어요.

```python
"""팔도구.py의 예제_팔을 URDF 글로 옮긴다. 3장 팔모델.py(MJCF)의 URDF판이다."""
from 팔도구 import 손끝_위치, 예제_팔

반지름 = 0.02         # 링크 막대의 반지름(m)
선밀도 = 2.0          # 링크 1m당 질량(kg/m). 예제용으로 정한 값


def 원기둥_관성(질량: float, 길이: float) -> tuple[float, float, float]:
    """z축 방향으로 꽉 찬 원기둥의 무게중심 기준 관성 (ixx, iyy, izz)."""
    옆 = 질량 * (3 * 반지름**2 + 길이**2) / 12
    return 옆, 옆, 질량 * 반지름**2 / 2


def 링크(이름: str, 길이: float) -> str:
    """길이만큼 z축 방향으로 뻗은 막대 링크. 보이는 모양·부딪히는 모양·질량을 함께 적는다."""
    질량 = 선밀도 * 길이
    ixx, iyy, izz = 원기둥_관성(질량, 길이)
    가운데 = f'<origin xyz="0 0 {길이 / 2:g}"/>'
    모양 = f'<geometry><cylinder radius="{반지름}" length="{길이:g}"/></geometry>'
    return (f'  <link name="{이름}">\n'
            f'    <visual>{가운데}{모양}</visual>\n'
            f'    <collision>{가운데}{모양}</collision>\n'
            f'    <inertial>{가운데}<mass value="{질량:g}"/>\n'
            f'      <inertia ixx="{ixx:.6g}" ixy="0" ixz="0" iyy="{iyy:.6g}" iyz="0" izz="{izz:.6g}"/></inertial>\n'
            f'  </link>')


def 관절(이름: str, 부모: str, 자식: str, 위치, 축=None) -> str:
    """축이 있으면 회전 관절(revolute), 없으면 고정 관절(fixed)."""
    xyz = " ".join(f"{값:g}" for 값 in 위치)
    줄들 = [f'  <joint name="{이름}" type="{"revolute" if 축 else "fixed"}">',
          f'    <parent link="{부모}"/><child link="{자식}"/>',
          f'    <origin xyz="{xyz}" rpy="0 0 0"/>']
    if 축:
        줄들 += [f'    <axis xyz="{" ".join(f"{값:g}" for 값 in 축)}"/>',
               '    <limit lower="-3.14159" upper="3.14159" effort="10" velocity="2"/>']
    return "\n".join(줄들 + ["  </joint>"])


def URDF(팔=예제_팔, 손끝=손끝_위치) -> str:
    """바닥(base_link) → link1 … link6 → 손끝(tip). 관절 i는 link(i-1)과 link(i)를 잇는다."""
    길이들 = [위치[2] for _, 위치, _ in 팔] + [손끝[2]]     # 이 팔은 모든 링크가 z축 방향
    부분들 = [링크("base_link", 길이들[0])]
    for i, (_, 위치, 축) in enumerate(팔, start=1):
        부모 = "base_link" if i == 1 else f"link{i - 1}"
        부분들 += [관절(f"joint{i}", 부모, f"link{i}", 위치, 축), 링크(f"link{i}", 길이들[i])]
    부분들 += [관절("tip_joint", f"link{len(팔)}", "tip", 손끝), '  <link name="tip"/>']
    return '<?xml version="1.0"?>\n<robot name="arm6">\n' + "\n".join(부분들) + "\n</robot>\n"
```

`관절` 함수의 `origin`에 `rpy="0 0 0"`이 붙어 있는 것에 주목하세요. 3장의 예제 팔은 일부러 고정 자세가 없도록 만들었기 때문에(3장 3.3절) `rpy`가 모두 0이고, 관절마다 `axis`로 회전축을 정했습니다. 6.9절에서 볼 실제 로봇 팔 URDF는 반대로 `axis`를 모두 z축으로 두고 `rpy`로 관절 좌표계를 돌려 놓는 경우가 많아요. 둘 다 같은 팔을 적는 올바른 방법입니다.

### URDF로 순기구학

URDF를 읽어 손끝 위치를 계산하는 함수도 만들어 둡시다. 할 일은 3장의 `순기구학`과 같습니다. 뿌리에서 손끝까지 관절을 따라가며 `원점_변환(origin) @ 관절_움직임(관절, 값)`을 곱해요. 다른 점은 고정 자세(`rpy`)와 관절 종류를 URDF에서 읽는다는 것뿐입니다. `robot_state_publisher`가 안에서 하는 일이 바로 이것이에요.

```python
"""URDF를 읽어 순기구학을 계산한다. robot_state_publisher가 안에서 하는 일을 파이썬으로."""
import numpy as np
from scipy.spatial.transform import Rotation

from 팔도구 import 변환, 이동, 축_회전


def 원점_변환(origin) -> np.ndarray:
    """joint의 <origin xyz rpy>: 고정 축 롤→피치→요, 곧 Rz(요) @ Ry(피치) @ Rx(롤) (2장 2.4절)."""
    if origin is None:                                   # origin을 안 적으면 제자리
        return np.eye(4)
    xyz = origin.xyz or [0.0, 0.0, 0.0]
    rpy = origin.rpy or [0.0, 0.0, 0.0]
    return 변환(Rotation.from_euler("xyz", rpy).as_matrix(), xyz)


def 관절_움직임(관절, 값: float) -> np.ndarray:
    """관절 값만큼의 움직임: 회전 관절은 축을 중심으로 돌고, 직선 관절은 축을 따라 미끄러진다."""
    축 = np.array(관절.axis if 관절.axis is not None else [1.0, 0.0, 0.0])   # axis 기본값은 x축
    if 관절.type in ("revolute", "continuous"):
        return 축_회전(축, 값)
    if 관절.type == "prismatic":
        return 이동(축 * 값)
    return np.eye(4)                                     # fixed


def URDF_순기구학(로봇, 관절값: dict[str, float], 끝: str, 시작: str | None = None) -> np.ndarray:
    """시작 링크(기본은 뿌리)에서 끝 링크까지 joint를 따라가며 곱한 T_시작_끝."""
    시작 = 시작 or 로봇.get_root()
    T = np.eye(4)
    for 이름 in 로봇.get_chain(시작, 끝, links=False):    # 지나가는 joint 이름들
        관절 = 로봇.joint_map[이름]
        T = T @ 원점_변환(관절.origin) @ 관절_움직임(관절, 관절값.get(이름, 0.0))
    return T
```

`원점_변환`은 6.2절에서 확인한 대로 `rpy`를 SciPy 소문자 `"xyz"`로 바꿉니다. 직선 관절은 축 방향으로 값(m)만큼 옮기고, 회전 관절은 3장의 `축_회전`으로 돌려요. `axis`를 안 적으면 6.1절의 표대로 x축을 씁니다.

이제 만든 URDF를 읽어 3장의 순기구학과 비교하겠습니다.

```python
import numpy as np
from urdf_parser_py.urdf import URDF as URDF읽기

from urdf기구학 import URDF_순기구학
from 팔도구 import 순기구학
from 팔URDF import URDF
from 회전도구 import 깔끔

글 = URDF()
print("만든 URDF:", len(글.splitlines()), "줄")
print("\n".join(글.splitlines()[8:14]))                  # joint1 부분만 보기

로봇 = URDF읽기.from_xml_string(글)
print("사슬:", 로봇.get_chain("base_link", "tip", links=False))

관절각 = np.deg2rad([30, 45, 60, 0, 45, 0])                 # 3장 3.3절의 자세
값들 = {f"joint{i + 1}": 각 for i, 각 in enumerate(관절각)}
print("URDF로 계산한 손끝:", 깔끔(URDF_순기구학(로봇, 값들, "tip")[:3, 3]))
print("3장 순기구학 손끝 :", 깔끔(순기구학(관절각)[-1][:3, 3]))

생성기 = np.random.default_rng(0)
최대_차이 = 0.0
for _ in range(100):                                       # 아무 자세 100개로 비교
    q = 생성기.uniform(-np.pi, np.pi, size=6)
    T = URDF_순기구학(로봇, {f"joint{i + 1}": 각 for i, 각 in enumerate(q)}, "tip")
    최대_차이 = max(최대_차이, np.abs(T - 순기구학(q)[-1]).max())
print(f"자세 100개, 4×4 행렬 최대 차이: {최대_차이:.1e}")
```

```text
만든 URDF: 86 줄
  <joint name="joint1" type="revolute">
    <parent link="base_link"/><child link="link1"/>
    <origin xyz="0 0 0.1" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.14159" upper="3.14159" effort="10" velocity="2"/>
  </joint>
사슬: ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6', 'tip_joint']
URDF로 계산한 손끝: [0.478 0.276 0.248]
3장 순기구학 손끝 : [0.478 0.276 0.248]
자세 100개, 4×4 행렬 최대 차이: 0.0e+00
```

86줄짜리 URDF가 만들어졌고, 3장 3.3절의 자세 (30, 45, 60, 0, 45, 0)도에서 손끝이 3장과 같은 (0.478, 0.276, 0.248)에 왔습니다. 아무 자세 100개에서 4×4 행렬의 차이가 정확히 0이에요. 두 함수가 같은 계산을 같은 순서로 하니 반올림 오차조차 없습니다. 목록에서 URDF로 옮기는 동안 정보가 빠지지 않았다는 뜻이에요.

## 6.5 xacro: 반복을 줄이는 매크로

### 복사해 붙이기의 함정

`두관절팔.urdf`의 위팔과 아래팔은 숫자 몇 개만 빼고 똑같았습니다. 6자유도 팔이면 이런 덩어리가 일곱 번 나와요. 막대 반지름을 0.02에서 0.025로 바꾸려면 열네 곳(visual, collision)을 고쳐야 하고, 관성까지 다시 계산해야 합니다. 하나만 빠뜨려도 모양과 관성이 어긋난 팔이 되죠.

6.4절에서는 파이썬으로 URDF 글을 만들어 이 문제를 피했습니다. ROS에는 같은 일을 하는 표준 도구가 있는데, 바로 **xacro**(XML macro)예요. URDF 안에 변수와 함수 비슷한 것을 쓸 수 있게 해 주고, `xacro` 명령이 이것을 펼쳐 보통 URDF로 만들어 줍니다. 파이썬 코드 없이 파일 하나로 끝나니, 다른 사람과 로봇을 주고받을 때는 xacro가 편해요. 대부분의 공개 로봇 패키지가 `.urdf.xacro` 파일로 로봇을 배포합니다.

xacro의 기능은 세 가지만 알면 충분합니다.

| 요소 | 하는 일 | 쓰는 법 |
|---|---|---|
| `xacro:property` | 이름 붙인 값(상수) | `<xacro:property name="radius" value="0.02"/>` → `${radius}` |
| `xacro:macro` | 매개변수를 받는 덩어리(함수) | `<xacro:macro name="segment" params="i parent ...">` → `<xacro:segment i="1" .../>` |
| `xacro:arg` | 명령줄에서 바꾸는 값 | `<xacro:arg name="tool_length" default="0.05"/>` → `$(arg tool_length)` |

`${...}` 안에는 계산식을 쓸 수 있어요. xacro가 파이썬으로 만들어져 있어서 `**`(거듭제곱)이나 `pi` 같은 파이썬 식을 그대로 씁니다. 예제 팔을 xacro로 적으면 이렇습니다. `예제팔.urdf.xacro`로 저장하세요.

```xml
<?xml version="1.0"?>
<!-- 3장의 예제 6자유도 팔을 xacro로: 마디 하나를 매크로로 만들고 여섯 번 부른다 -->
<robot name="arm6" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <xacro:arg name="tool_length" default="0.05"/>          <!-- 명령줄에서 바꿀 수 있는 값 -->
  <xacro:property name="radius" value="0.02"/>            <!-- 링크 막대 반지름(m) -->
  <xacro:property name="density" value="2.0"/>            <!-- 링크 1m당 질량(kg/m) -->

  <!-- z축 방향으로 length만큼 뻗은 막대 링크 -->
  <xacro:macro name="rod_link" params="name length">
    <xacro:property name="m" value="${density * length}"/>
    <link name="${name}">
      <visual>
        <origin xyz="0 0 ${length / 2}"/>
        <geometry><cylinder radius="${radius}" length="${length}"/></geometry>
      </visual>
      <collision>
        <origin xyz="0 0 ${length / 2}"/>
        <geometry><cylinder radius="${radius}" length="${length}"/></geometry>
      </collision>
      <inertial>
        <origin xyz="0 0 ${length / 2}"/>
        <mass value="${m}"/>
        <inertia ixx="${m * (3 * radius**2 + length**2) / 12}" ixy="0" ixz="0"
                 iyy="${m * (3 * radius**2 + length**2) / 12}" iyz="0" izz="${m * radius**2 / 2}"/>
      </inertial>
    </link>
  </xacro:macro>

  <!-- 마디 하나 = 회전 관절 joint{i} + 그 뒤의 링크 link{i} -->
  <xacro:macro name="segment" params="i parent offset axis length">
    <joint name="joint${i}" type="revolute">
      <parent link="${parent}"/>
      <child link="link${i}"/>
      <origin xyz="0 0 ${offset}" rpy="0 0 0"/>
      <axis xyz="${axis}"/>
      <limit lower="${-pi}" upper="${pi}" effort="10" velocity="2"/>
    </joint>
    <xacro:rod_link name="link${i}" length="${length}"/>
  </xacro:macro>

  <xacro:rod_link name="base_link" length="0.10"/>
  <xacro:segment i="1" parent="base_link" offset="0.10" axis="0 0 1" length="0.10"/>
  <xacro:segment i="2" parent="link1" offset="0.10" axis="0 1 0" length="0.30"/>
  <xacro:segment i="3" parent="link2" offset="0.30" axis="0 1 0" length="0.25"/>
  <xacro:segment i="4" parent="link3" offset="0.25" axis="0 0 1" length="0.05"/>
  <xacro:segment i="5" parent="link4" offset="0.05" axis="0 1 0" length="0.05"/>
  <xacro:segment i="6" parent="link5" offset="0.05" axis="0 0 1" length="$(arg tool_length)"/>

  <joint name="tip_joint" type="fixed">
    <parent link="link6"/>
    <child link="tip"/>
    <origin xyz="0 0 $(arg tool_length)"/>
  </joint>
  <link name="tip"/>
</robot>
```

`rod_link` 매크로는 6.4절의 `링크` 함수, `segment` 매크로는 "관절 하나 + 그 뒤의 링크 하나"입니다. 맨 아래 일곱 줄만 보면 3장의 `예제_팔` 목록처럼 팔 전체가 한눈에 들어와요. 관성 공식도 매크로 안에 한 번만 적었으니 반지름을 바꾸면 관성이 따라 바뀝니다. 마지막 링크 길이와 손끝 위치는 `tool_length` 인자로 빼서, 도구를 바꿔 끼울 때 명령줄에서 고칠 수 있게 했어요.

### 펼쳐 보기

`xacro` 명령으로 펼쳐서 결과를 확인합니다.

```bash
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
```

```text
  55 예제팔.urdf.xacro
 190 /tmp/arm6.urdf
 245 total
--- 펼쳐진 joint3 ---
  <joint name="joint3" type="revolute">
    <parent link="link2"/>
    <child link="link3"/>
    <origin rpy="0 0 0" xyz="0 0 0.3"/>
    <axis xyz="0 1 0"/>
    <limit effort="10" lower="-3.141592653589793" upper="3.141592653589793" velocity="2"/>
  </joint>
--- check_urdf ---
root Link: base_link has 1 child(ren)
    child(1):  link1
        child(1):  link2
            child(1):  link3
                child(1):  link4
                    child(1):  link5
                        child(1):  link6
                            child(1):  tip
--- 명령줄에서 tool_length:=0.12 ---
  <joint name="tip_joint" type="fixed">
    <parent link="link6"/>
    <child link="tip"/>
    <origin xyz="0 0 0.12"/>
  </joint>
```

55줄짜리 xacro가 190줄짜리 URDF로 펼쳐졌습니다. 6.4절의 파이썬판(86줄)보다 긴 건 xacro가 요소마다 줄을 바꿔 보기 좋게 적기 때문이에요. `joint3`을 보면 `${-pi}`가 -3.141592653589793으로 계산되어 들어갔고, `check_urdf`도 통과했습니다. `tool_length:=0.12`를 주자 손끝 관절이 0.12m로 바뀌었어요. 펼친 파일 맨 위에는 "xacro가 만든 파일이니 손으로 고치지 말라"는 주석이 붙습니다. 고칠 때는 늘 `.xacro` 쪽을 고치고 다시 펼치세요.

파이썬으로 만든 URDF와 xacro로 만든 URDF가 정말 같은 팔인지 확인해 봅시다.

```python
import subprocess
from pathlib import Path

import numpy as np
from urdf_parser_py.urdf import URDF as URDF읽기

from urdf기구학 import URDF_순기구학
from 팔URDF import URDF

xacro_글 = subprocess.run(["xacro", str(Path(__file__).with_name("예제팔.urdf.xacro"))],
                         capture_output=True, text=True, check=True).stdout
가 = URDF읽기.from_xml_string(xacro_글)       # xacro로 만든 것
나 = URDF읽기.from_xml_string(URDF())         # 파이썬(팔URDF.py)으로 만든 것

print("링크 이름이 같은가?", [l.name for l in 가.links] == [l.name for l in 나.links])
for 이름 in ["joint3", "joint6", "tip_joint"]:
    j가, j나 = 가.joint_map[이름], 나.joint_map[이름]
    print(f"{이름}: 위치 {j가.origin.xyz} == {j나.origin.xyz}, 축 {j가.axis} == {j나.axis}")
관성_차이 = max(abs(getattr(a.inertial.inertia, k) - getattr(b.inertial.inertia, k))
              for a, b in zip(가.links, 나.links) if a.inertial for k in ["ixx", "iyy", "izz"])
print(f"관성 값 최대 차이: {관성_차이:.1e}")

q = {f"joint{i + 1}": 각 for i, 각 in enumerate(np.deg2rad([30, 45, 60, 0, 45, 0]))}
print("손끝이 같은가?", np.allclose(URDF_순기구학(가, q, "tip"), URDF_순기구학(나, q, "tip")))
```

```text
링크 이름이 같은가? True
joint3: 위치 [0.0, 0.0, 0.3] == [0.0, 0.0, 0.3], 축 [0.0, 1.0, 0.0] == [0.0, 1.0, 0.0]
joint6: 위치 [0.0, 0.0, 0.05] == [0.0, 0.0, 0.05], 축 [0.0, 0.0, 1.0] == [0.0, 0.0, 1.0]
tip_joint: 위치 [0.0, 0.0, 0.05] == [0.0, 0.0, 0.05], 축 None == None
관성 값 최대 차이: 3.3e-09
손끝이 같은가? True
```

링크 이름, 관절 위치와 축, 손끝 위치가 모두 같습니다. 관성 값만 3.3e-09만큼 다른데, 6.4절의 `팔URDF.py`가 숫자를 유효 숫자 여섯 자리(`:.6g`)로 줄여 적었기 때문이에요. xacro는 파이썬 실수를 그대로 다 적었습니다.

> **Q. 파이썬으로 URDF를 만들면 되는데 xacro를 꼭 배워야 하나요?**
> 내 로봇만 쓴다면 어느 쪽이든 괜찮습니다. 하지만 공개된 로봇 패키지, 그리퍼, 센서 받침대는 대부분 xacro 매크로로 배포되고, `xacro:include`로 남의 매크로 파일을 불러와 내 로봇에 붙이는 일이 흔해요. 이 장의 세 요소에 `xacro:include`와 조건문 `xacro:if`만 더하면 공개된 xacro 파일 대부분을 읽을 수 있습니다.

## 6.6 robot_state_publisher: 관절 각도를 좌표계 나무로

### 누가 손끝 위치를 알려 주나

URDF는 설계도일 뿐, 지금 팔이 어떤 자세인지는 모릅니다. 관절 각도는 로봇이 움직이는 동안 계속 바뀌니까요. ROS 2에서는 두 노드가 손을 잡고 이 일을 합니다.

- **joint_state_publisher**: 관절 각도를 `/joint_states` 토픽(`sensor_msgs/msg/JointState`: 관절 이름 목록과 각도 목록)으로 발행한다. 실제 로봇에서는 이 자리를 7장에서 볼 서보 드라이버 노드가 차지하고, 연습할 때는 이 노드가 정해 둔 각도를 대신 발행한다
- **robot_state_publisher**: URDF(`robot_description` 파라미터)와 `/joint_states`를 받아, 링크마다 "부모 기준 자식의 포즈"를 계산해 **tf2**로 내보낸다. 움직이는 관절의 변환은 `/tf` 토픽으로, 고정 관절의 변환은 `/tf_static` 토픽으로 보낸다

**tf2**는 ROS의 좌표계 관리자입니다. 여러 노드가 "카메라는 손목에서 어디", "손목은 팔꿈치에서 어디"를 각자 알려 주면, tf2가 이것들을 모아 좌표계 나무를 만들고 "바닥에서 본 카메라는 어디?" 같은 질문에 답해 줘요. 2장 2.8절에서 손으로 하던 변환 사슬 곱하기를 대신해 주는 셈입니다.

두관절팔로 두 노드를 띄워 봅시다. `joint_state_publisher`는 처음 각도를 `zeros` 파라미터로 받을 수 있어서, 어깨 30도(0.5236rad), 팔꿈치 45도(0.7854rad)를 주었습니다. `&`로 노드를 뒤에서 돌리고, 확인이 끝나면 `kill`로 내려요.

```bash
# 두관절팔.urdf로 robot_state_publisher와 joint_state_publisher를 띄우고 들여다본다
cd "$(dirname "$0")"
ros2 run robot_state_publisher robot_state_publisher \
    --ros-args -p robot_description:="$(cat 두관절팔.urdf)" > /dev/null 2>&1 &
ros2 run joint_state_publisher joint_state_publisher \
    --ros-args -p zeros.shoulder:=0.5236 -p zeros.elbow:=0.7854 > /dev/null 2>&1 &
sleep 3                                       # 노드들이 뜨고 서로 찾을 시간
echo "--- 노드 ---";  ros2 node list
echo "--- 토픽 ---";  ros2 topic list
echo "--- /joint_states 한 번 ---"
ros2 topic echo --once /joint_states --field name
ros2 topic echo --once /joint_states --field position
echo "--- tf2_echo base_link tip ---"
timeout 3 ros2 run tf2_ros tf2_echo base_link tip 2> /dev/null | grep -m1 -A8 "Translation"
kill %1 %2
```

```text
--- 노드 ---
/joint_state_publisher
/robot_state_publisher
--- 토픽 ---
/joint_states
/parameter_events
/robot_description
/rosout
/tf
/tf_static
--- /joint_states 한 번 ---
['shoulder', 'elbow']
---
array('d', [0.5236, 0.7854])
---
--- tf2_echo base_link tip ---
- Translation: [0.424, 0.490, 0.050]
- Rotation: in Quaternion (xyzw) [0.000, 0.000, 0.609, 0.793]
- Rotation: in RPY (radian) [0.000, -0.000, 1.309]
- Rotation: in RPY (degree) [0.000, -0.000, 75.000]
- Matrix:
  0.259 -0.966  0.000  0.424
  0.966  0.259  0.000  0.490
  0.000  0.000  1.000  0.050
  0.000  0.000  0.000  1.000
```

노드 둘이 떴고, 토픽 목록에 `/joint_states`, `/robot_description`, `/tf`, `/tf_static`이 생겼습니다. `robot_state_publisher`는 받은 URDF를 `/robot_description` 토픽으로도 다시 내보내는데, `joint_state_publisher`가 이 토픽에서 URDF를 읽어 관절 이름(`shoulder`, `elbow`)을 알아냈어요. 고정 관절 `tip_joint`는 움직이지 않으니 `/joint_states`에 들어 있지 않습니다.

마지막 `tf2_echo base_link tip`은 tf2에게 "base_link에서 본 tip"을 물은 결과예요. 이동 부분 (0.424, 0.490, 0.050)은 3장 들어가며의 "어깨 30도, 팔꿈치 45도 → 손끝 (0.424, 0.49)"와 같고, 높이 0.05는 어깨가 바닥에서 0.05m 위에 있어서 생겼습니다. 회전은 z축으로 75도(30 + 45)예요. 쿼터니언이 `(xyzw)` 순서로 찍힌 것도 보세요. 2장 2.6절의 표대로 ROS는 쿼터니언을 x, y, z, w 이름 칸으로 다룹니다.

### 파이썬에서 tf2에 묻기

명령줄 대신 파이썬 노드에서 관절 각도를 보내고 tf2에 물어보겠습니다. 이 장에서 계속 쓸 도구를 `tf도구.py`에 모았어요. 6.2절에서 미리 쓴 그 파일입니다.

```python
"""6장 도구: robot_state_publisher를 띄우고, 관절 각도를 보내고, tf2로 변환을 묻는다."""
import json
import subprocess
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from scipy.spatial.transform import Rotation
from sensor_msgs.msg import JointState
from tf2_ros import Buffer, TransformListener

여기 = Path(__file__).parent              # 이 파일과 URDF가 있는 폴더


@contextmanager
def 상태_발행기(urdf_글: str):
    """robot_state_publisher 노드를 따로 띄웠다가, with 블록이 끝나면 내린다.
    URDF 글은 파라미터 파일로 넘긴다. 명령줄 -p로 넘기면 xacro가 붙인 머리 주석 때문에 해석에 실패한다."""
    with tempfile.NamedTemporaryFile("w", suffix=".yaml") as 파일:
        설정 = {"robot_state_publisher": {"ros__parameters": {"robot_description": urdf_글}}}
        json.dump(설정, 파일)                          # JSON은 YAML로도 읽힌다
        파일.flush()
        명령 = ["ros2", "run", "robot_state_publisher", "robot_state_publisher",
              "--ros-args", "--params-file", 파일.name]
        프로세스 = subprocess.Popen(명령, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            yield 프로세스
        finally:
            프로세스.terminate()
            프로세스.wait()


def 행렬로(변환_메시지) -> np.ndarray:
    """TransformStamped → 4×4 동차 변환 행렬. ROS 쿼터니언은 x, y, z, w 이름 칸이다."""
    t, q = 변환_메시지.transform.translation, 변환_메시지.transform.rotation
    T = np.eye(4)
    T[:3, :3] = Rotation.from_quat([q.x, q.y, q.z, q.w]).as_matrix()
    T[:3, 3] = [t.x, t.y, t.z]
    return T


class 팔연결(Node):
    """/joint_states로 관절 각도를 보내고, tf2 버퍼에서 변환을 꺼내는 노드."""

    def __init__(self) -> None:
        super().__init__("arm_client")
        self.발행기 = self.create_publisher(JointState, "joint_states", 10)
        self.버퍼 = Buffer()
        self.듣개 = TransformListener(self.버퍼, self, spin_thread=True)   # 받는 일은 따로 도는 스레드가
        마감 = time.monotonic() + 10
        while self.발행기.get_subscription_count() == 0:                  # 받는 쪽이 붙을 때까지
            if time.monotonic() > 마감:
                raise TimeoutError("joint_states를 받는 노드(robot_state_publisher)가 없다")
            time.sleep(0.05)

    def 관절_보내기(self, 이름들: list[str], 각들, 확인=("base_link", "tip")) -> Time:
        """관절 각도(rad)를 발행하고 메시지에 찍은 시각을 돌려준다.
        처음 몇 번은 받는 쪽이 아직 연결 중이라 놓칠 수 있어서, tf2에 그 시각의 변환이 생길 때까지 다시 보낸다."""
        while True:
            지금 = self.get_clock().now()
            메시지 = JointState(name=list(이름들), position=[float(각) for 각 in 각들])
            메시지.header.stamp = 지금.to_msg()
            self.발행기.publish(메시지)
            if self.버퍼.can_transform(*확인, 지금, timeout=Duration(seconds=0.2)):
                return 지금

    def 변환(self, 기준: str, 대상: str, 시각: Time | None = None) -> np.ndarray:
        """tf2에 묻는다: 대상 좌표계를 기준 좌표계에서 본 4×4 변환(T_기준_대상)."""
        메시지 = self.버퍼.lookup_transform(기준, 대상, 시각 or Time(), timeout=Duration(seconds=5))
        return 행렬로(메시지)


@contextmanager
def 연결():
    """rclpy를 켜고 팔연결 노드 하나를 만든다."""
    rclpy.init()
    노드 = 팔연결()
    try:
        yield 노드
    finally:
        노드.destroy_node()
        rclpy.shutdown()
```

세 가지를 담았습니다.

- **`상태_발행기`**: `robot_state_publisher`를 띄웠다가 `with` 블록이 끝나면 내리는 컨텍스트 관리자(1권 15장의 `@contextmanager`)입니다. URDF 글은 **파라미터 파일**로 넘겨요. xacro가 펼친 URDF는 머리 주석에 `|` 같은 글자가 있어서, 명령줄 `-p`로 넘기면 `Couldn't parse parameter override rule` 오류와 함께 노드가 죽습니다. 손으로 쓴 `두관절팔.urdf`는 앞의 예제처럼 `-p`로도 넘어가요
- **`팔연결`**: `/joint_states`를 발행하는 노드입니다. tf2의 `Buffer`(받은 변환을 시간과 함께 쌓아 두는 곳)와 `TransformListener`(`/tf`, `/tf_static`을 받아 버퍼에 넣는 일꾼)를 함께 들고 있어요. `spin_thread=True`를 주면 받는 일을 따로 도는 스레드가 맡아서, 우리는 순서대로 코드를 짜도 됩니다
- **`관절_보내기`**: 관절 각도를 보내고 메시지에 찍은 **시각**을 돌려줍니다. 노드들이 막 서로를 찾은 순간에는 첫 메시지가 상대에게 닿지 않을 수 있어서, 그 시각의 변환이 tf2 버퍼에 들어올 때까지 다시 보내요. 돌려받은 시각으로 `변환`을 물으면 "바로 그 각도일 때의 변환"을 정확히 꺼낼 수 있습니다

이제 6자유도 예제 팔을 xacro로 펼쳐 띄우고, 3장의 순기구학과 비교합니다.

```python
import subprocess

import numpy as np
import yaml

from tf도구 import 상태_발행기, 연결, 여기
from 팔도구 import 순기구학
from 회전도구 import 깔끔

urdf = subprocess.run(["xacro", str(여기 / "예제팔.urdf.xacro")], capture_output=True, text=True, check=True).stdout
관절_이름 = [f"joint{i}" for i in range(1, 7)]

with 상태_발행기(urdf), 연결() as 팔:
    관절각 = np.deg2rad([30, 45, 60, 0, 45, 0])
    시각 = 팔.관절_보내기(관절_이름, 관절각)
    T_바닥_손끝 = 팔.변환("base_link", "tip", 시각)
    print("tf2가 알려 준 손끝:", 깔끔(T_바닥_손끝[:3, 3]))
    print("3장 순기구학 손끝 :", 깔끔(순기구학(관절각)[-1][:3, 3]))
    print("link3 원점(tf2)   :", 깔끔(팔.변환("base_link", "link3", 시각)[:3, 3]))

    생성기 = np.random.default_rng(0)
    최대_차이 = 0.0
    for _ in range(20):                                   # 아무 자세 20개
        q = 생성기.uniform(-np.pi, np.pi, size=6)
        시각 = 팔.관절_보내기(관절_이름, q)
        최대_차이 = max(최대_차이, np.abs(팔.변환("base_link", "tip", 시각) - 순기구학(q)[-1]).max())
    print(f"자세 20개, tf2와 3장 순기구학의 최대 차이: {최대_차이:.1e}")

    # 버퍼가 아는 좌표계 나무: 좌표계마다 부모 하나. 시각이 0인 것은 /tf_static으로 온 정적 변환
    나무 = yaml.safe_load(팔.버퍼.all_frames_as_yaml())
    사슬 = ["tip"]
    while 사슬[-1] in 나무:
        사슬.append(나무[사슬[-1]]["parent"])
    print(" → ".join(f"{이름}(정적)" if 이름 in 나무 and 나무[이름]["most_recent_transform"] == 0 else 이름
                     for 이름 in reversed(사슬)))
```

```text
tf2가 알려 준 손끝: [0.478 0.276 0.248]
3장 순기구학 손끝 : [0.478 0.276 0.248]
link3 원점(tf2)   : [0.184 0.106 0.412]
자세 20개, tf2와 3장 순기구학의 최대 차이: 4.4e-16
base_link → link1 → link2 → link3 → link4 → link5 → link6 → tip(정적)
```

tf2가 알려 준 손끝이 3장의 (0.478, 0.276, 0.248)과 같고, 팔꿈치 링크(`link3`)의 원점도 3장 3.3절에서 계산한 팔꿈치 관절 위치 (0.184, 0.106, 0.412)와 같습니다. 아무 자세 20개에서 차이가 4.4e-16m, 반올림 오차뿐이에요. 3장 3.9절에서 MuJoCo로 한 검산을 이번에는 ROS의 tf2로 한 셈입니다. 우리 손으로 짠 순기구학, MuJoCo, ROS가 모두 같은 팔을 보고 있어요.

마지막 줄은 tf2 버퍼가 아는 좌표계 나무를 손끝에서 부모를 따라 올라가며 적은 것입니다. "(정적)"은 `link6 → tip` 변환이 `/tf_static`으로 왔다는 표시예요. 정적 변환은 시각 0으로 기록되고 어느 시각에 물어도 같은 값으로 쓰입니다.

### launch 파일로 한 번에

노드 둘(나중에는 화면 도구까지 셋)을 매번 따로 띄우기는 번거롭습니다. 5장에서 본 launch 파일로 묶어 두면 명령 한 줄로 끝나요. 다음 내용을 `팔보기.launch.py`로 저장하세요.

```python
"""예제 팔을 화면에 띄우는 launch 파일: xacro → robot_state_publisher, 관절 슬라이더 대신 joint_state_publisher, RViz."""
from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

xacro_파일 = Path(__file__).with_name("예제팔.urdf.xacro")


def generate_launch_description() -> LaunchDescription:
    # xacro를 실행한 결과 글을 그대로 파라미터 값으로(문자열이라고 못 박아 둔다)
    설명 = ParameterValue(Command(["xacro ", str(xacro_파일)]), value_type=str)
    return LaunchDescription([
        DeclareLaunchArgument("rviz", default_value="true"),
        Node(package="robot_state_publisher", executable="robot_state_publisher",
             parameters=[{"robot_description": 설명}]),
        Node(package="joint_state_publisher", executable="joint_state_publisher",
             parameters=[{"zeros.joint2": 0.7854, "zeros.joint3": 1.0472}]),
        Node(package="rviz2", executable="rviz2", condition=IfCondition(LaunchConfiguration("rviz"))),
    ])
```

xacro를 펼치는 일도 launch 파일이 맡습니다. `Command(["xacro ", 경로])`가 xacro 명령을 실행한 결과 글을 파라미터 값으로 넣어 주고, `ParameterValue(..., value_type=str)`가 그 값을 "그냥 문자열"로 못 박아서 앞에서 본 해석 실패를 피해요. 공개 로봇 패키지의 launch 파일에서 거의 언제나 이 두 줄을 볼 수 있습니다. `joint_state_publisher`에는 어깨 45도, 팔꿈치 60도를 처음 각도로 줬고, RViz(6.8절)는 `rviz` 인자가 참일 때만 띄우게 했습니다. 이 책의 실행 환경에는 화면이 없으니 `rviz:=false`로 띄워 확인해 볼게요.

```bash
# launch 파일 하나로 노드들을 띄운다. 화면이 없으니 RViz만 끄고(rviz:=false) tf를 확인한다
cd "$(dirname "$0")"
ros2 launch ./팔보기.launch.py rviz:=false > /dev/null 2>&1 &
sleep 4
ros2 node list
timeout 3 ros2 run tf2_ros tf2_echo base_link tip 2> /dev/null | grep -m1 "Translation"
kill %1
wait
```

```text
/joint_state_publisher
/robot_state_publisher
- Translation: [0.599, 0.000, 0.309]
```

두 노드가 떴고, 손끝은 (0.599, 0, 0.309)입니다. 3장의 `순기구학`에 (0, 45, 60, 0, 0, 0)도를 넣어도 같은 값이 나와요. 이 launch 파일은 화면이 있는 컴퓨터라면 `rviz:=false` 없이 그대로 RViz까지 띄웁니다.

## 6.7 tf2 들여다보기

### T_A_B와 (target, source)

이 장에서 가장 헷갈리는 곳을 짚고 넘어가겠습니다. 2장부터 우리는 변환에 `T_바닥_손끝`처럼 이름을 붙였죠. "손끝 기준 값을 받아 바닥 기준 값으로 바꾸는 변환", 다른 말로 "바닥에서 본 손끝의 포즈"입니다. tf2에서는 이것을 `버퍼.lookup_transform("base_link", "tip", 시각)`으로 묻습니다. `lookup_transform`의 정의를 보면 첫째 매개변수 이름이 `target_frame`, 둘째가 `source_frame`이에요. "source(손끝) 좌표계의 데이터를 target(바닥) 좌표계로 옮기는 변환"이라는 뜻입니다. 이 책의 이름 규칙과 순서가 같아요. **`T_A_B`는 `lookup_transform("A", "B")`** 입니다. 실행해서 확인해 보겠습니다.

```python
import numpy as np
import tf2_geometry_msgs  # noqa: F401  PointStamped를 tf2로 변환할 수 있게 등록한다
from geometry_msgs.msg import PointStamped
from rclpy.duration import Duration

from tf도구 import 상태_발행기, 연결, 여기, 행렬로
from 회전도구 import 깔끔

with 상태_발행기((여기 / "두관절팔.urdf").read_text()), 연결() as 팔:
    시각 = 팔.관절_보내기(["shoulder", "elbow"], np.deg2rad([30, 45]))
    메시지 = 팔.버퍼.lookup_transform("base_link", "tip", 시각)     # (target, source)
    print("lookup_transform('base_link', 'tip')")
    print("  header.frame_id =", 메시지.header.frame_id, "/ child_frame_id =", 메시지.child_frame_id)
    T_바닥_손끝 = 행렬로(메시지)
    print("  이동 부분 =", 깔끔(T_바닥_손끝[:3, 3]), "← 바닥에서 본 손끝 위치")
    T_손끝_바닥 = 행렬로(팔.버퍼.lookup_transform("tip", "base_link", 시각))
    print("순서를 바꾼 것은 역변환인가?", np.allclose(T_손끝_바닥, np.linalg.inv(T_바닥_손끝)))

    # 손끝 좌표계로 적은 점(손끝 앞 0.1m)을 바닥 좌표계로 옮기기
    점_손끝 = PointStamped()
    점_손끝.header.frame_id = "tip"
    점_손끝.header.stamp = 시각.to_msg()
    점_손끝.point.x = 0.1
    점_바닥 = 팔.버퍼.transform(점_손끝, "base_link", timeout=Duration(seconds=1))
    print("tf2가 옮긴 점    :", 깔끔(np.array([점_바닥.point.x, 점_바닥.point.y, 점_바닥.point.z])))
    print("T_바닥_손끝 @ 점 :", 깔끔((T_바닥_손끝 @ [0.1, 0, 0, 1])[:3]))
```

```text
lookup_transform('base_link', 'tip')
  header.frame_id = base_link / child_frame_id = tip
  이동 부분 = [0.424 0.49  0.05 ] ← 바닥에서 본 손끝 위치
순서를 바꾼 것은 역변환인가? True
tf2가 옮긴 점    : [0.45  0.586 0.05 ]
T_바닥_손끝 @ 점 : [0.45  0.586 0.05 ]
```

돌려받은 메시지의 `header.frame_id`가 `base_link`, `child_frame_id`가 `tip`입니다. 이동 부분은 바닥에서 본 손끝 위치(0.424, 0.49, 0.05)이고, 두 이름의 순서를 바꿔 물으면 정확히 역변환이 돌아왔어요. tf2의 `transform` 함수로 손끝 좌표계의 점(손끝 앞 0.1m)을 바닥 좌표계로 옮긴 결과도 `T_바닥_손끝 @ 점`과 같습니다. 손끝 x축이 75도 방향을 향하니, 0.1m 앞은 (0.424 + 0.1 cos 75°, 0.49 + 0.1 sin 75°) = (0.45, 0.586)이죠.

같은 변환이 곳곳에서 다른 이름으로 나타나니 표로 정리해 두겠습니다.

| 어디서 | "A에서 본 B" 적는 법 |
|---|---|
| 이 책의 이름 | `T_A_B` |
| tf2 파이썬 | `버퍼.lookup_transform("A", "B", 시각)` (target, source) |
| 변환 메시지 | `header.frame_id = "A"`, `child_frame_id = "B"` |
| 명령줄 | `ros2 run tf2_ros tf2_echo A B` |
| URDF 관절 | `<parent link="A"/>`, `<child link="B"/>` |
| static_transform_publisher | `--frame-id A --child-frame-id B` |

주의할 곳이 하나 있습니다. `tf2_echo`의 도움말은 첫째 인자를 **source_frame**, 둘째를 **target_frame**이라고 부릅니다. 파이썬 함수와 이름이 거꾸로예요. 그런데 도움말 설명을 끝까지 읽으면 "target 좌표계의 데이터를 source 좌표계로 가져오는 변환"이라고 되어 있어서, 결국 **위치는 같고 이름만 반대**입니다. 앞의 명령줄 예제에서 `tf2_echo base_link tip`이 바닥에서 본 손끝 (0.424, 0.490, 0.050)을 찍었던 것으로 확인할 수 있죠. 이름에 기대지 말고 "앞이 기준, 뒤가 대상"으로 기억하세요.

### 정적 변환과 동적 변환

tf2 나무의 가지는 두 종류입니다. 관절처럼 계속 바뀌는 **동적 변환**(`/tf`, 바뀔 때마다 새 시각으로 보낸다)과, 나사로 고정한 부품처럼 바뀌지 않는 **정적 변환**(`/tf_static`, 한 번만 보낸다)이에요. 정적 변환은 URDF의 `fixed` 관절에서도 오고, URDF 밖에서 `static_transform_publisher`로 따로 보탤 수도 있습니다.

2장의 카메라를 다시 불러와 보죠. 이번에는 카메라를 팔의 손목(`link6`) 좌표계에서 x축으로 4cm, 도구 방향(z축)으로 2cm 떨어진 곳에 나사로 고정하고, 렌즈(z축)는 도구 방향 그대로 두되 손목 축을 중심으로 90도 돌려 달았다고 합시다. URDF를 고치지 않고 정적 변환 하나만 보태면, 팔이 움직일 때 tf2가 동적 사슬과 정적 변환을 이어 "바닥에서 본 카메라"를 계산해 줍니다. 카메라가 렌즈 앞 0.25m에서 컵을 봤을 때 컵이 바닥 기준 어디인지, 두 자세에서 tf2와 행렬 계산으로 각각 구해 보겠습니다.

```python
import subprocess

import numpy as np

from tf도구 import 상태_발행기, 연결, 여기
from 팔도구 import 변환, 순기구학
from 회전도구 import Rz, 깔끔

urdf = subprocess.run(["xacro", str(여기 / "예제팔.urdf.xacro")], capture_output=True, text=True, check=True).stdout
관절_이름 = [f"joint{i}" for i in range(1, 7)]
# 손목(link6) 옆 4cm에 카메라를 나사로 고정했다: 정적 변환. 렌즈(z)는 도구 방향, 90도 돌려 달았다
카메라_설치 = subprocess.Popen(
    ["ros2", "run", "tf2_ros", "static_transform_publisher", "--x", "0.04", "--z", "0.02",
     "--yaw", str(np.pi / 2), "--frame-id", "link6", "--child-frame-id", "camera"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
T_손목_카메라 = 변환(Rz(90), [0.04, 0.0, 0.02])             # 같은 설치를 행렬로
컵_카메라 = np.array([0.02, -0.01, 0.25, 1.0])              # 카메라가 본 컵(카메라 기준)

with 상태_발행기(urdf), 연결() as 팔:
    for 관절각_도 in [[30, 45, 60, 0, 45, 0], [-20, 30, 70, 0, 60, 0]]:
        관절각 = np.deg2rad(관절각_도)
        시각 = 팔.관절_보내기(관절_이름, 관절각)
        T_바닥_카메라 = 팔.변환("base_link", "camera", 시각)          # 동적 사슬 + 정적 변환
        직접 = 순기구학(관절각)[5] @ T_손목_카메라                  # T_바닥_손목 @ T_손목_카메라
        print(f"자세 {관절각_도}")
        print("  tf2로 구한 바닥 기준 컵:", 깔끔((T_바닥_카메라 @ 컵_카메라)[:3]))
        print("  행렬로 구한 바닥 기준 컵:", 깔끔((직접 @ 컵_카메라)[:3]))
카메라_설치.terminate()
카메라_설치.wait()
```

```text
자세 [30, 45, 60, 0, 45, 0]
  tf2로 구한 바닥 기준 컵: [0.526 0.327 0.032]
  행렬로 구한 바닥 기준 컵: [0.526 0.327 0.032]
자세 [-20, 30, 70, 0, 60, 0]
  tf2로 구한 바닥 기준 컵: [ 0.484 -0.155  0.09 ]
  행렬로 구한 바닥 기준 컵: [ 0.484 -0.155  0.09 ]
```

두 자세 모두 tf2의 답과 행렬 계산(3장의 `순기구학`이 준 `T_바닥_손목` @ `T_손목_카메라`)이 같습니다. 정적 변환은 처음에 한 번 보냈을 뿐인데, 팔이 두 번째 자세로 움직이자 카메라 좌표계도 따라 움직였어요. tf2는 질문을 받을 때마다 나무를 따라 그 시각의 변환들을 곱하기 때문입니다. 2장 2.8절에서 `T_방_로봇 @ T_로봇_카메라`로 손수 하던 일을 tf2가 시간까지 맞춰 가며 대신해 주는 거예요.

### 시간을 기억하는 버퍼

tf2의 버퍼는 변환을 **시각과 함께** 쌓아 둡니다(기본 10초). 그래서 "지금"뿐 아니라 "0.3초 전 카메라 사진을 찍던 순간의 카메라 위치"도 물을 수 있어요. 카메라 영상처럼 찍힌 시각이 중요한 데이터를 팔의 자세와 맞출 때 이 기능이 쓰입니다. 노드 없이 버퍼만 만들어서, 시각을 정해 둔 변환을 직접 넣고 물어보겠습니다.

```python
import numpy as np
from geometry_msgs.msg import TransformStamped
from rclpy.time import Time
from scipy.spatial.transform import Rotation
from tf2_ros import Buffer, ExtrapolationException


def 변환_메시지(부모: str, 자식: str, 초: float, 요_도: float, x: float = 0.0) -> TransformStamped:
    """부모 기준 자식의 포즈: x만큼 옮기고 z축으로 요_도만큼 돈 것. 시각은 초."""
    메시지 = TransformStamped()
    메시지.header.frame_id, 메시지.child_frame_id = 부모, 자식
    메시지.header.stamp = Time(seconds=초).to_msg()
    메시지.transform.translation.x = x
    q = Rotation.from_euler("z", 요_도, degrees=True).as_quat()        # x, y, z, w 순서
    r = 메시지.transform.rotation
    r.x, r.y, r.z, r.w = q
    return 메시지


버퍼 = Buffer()                                     # 노드 없이 버퍼만 써 본다
버퍼.set_transform(변환_메시지("base_link", "link1", 1.0, 0), "실험")    # 1초: 0도
버퍼.set_transform(변환_메시지("base_link", "link1", 2.0, 90), "실험")   # 2초: 90도
버퍼.set_transform_static(변환_메시지("link1", "tip", 0.0, 0, x=0.5), "실험")  # 손끝은 0.5m 앞에 고정

for 초 in [1.0, 1.25, 1.5, 2.0]:
    t = 버퍼.lookup_transform("base_link", "tip", Time(seconds=초)).transform.translation
    각 = np.rad2deg(np.arctan2(t.y, t.x))
    print(f"{초:4.2f}초의 손끝: ({t.x:.3f}, {t.y:.3f}), 허리 {각:4.1f}도")
최신 = 버퍼.lookup_transform("base_link", "tip", Time())
print("Time()으로 물으면 가장 최근 것:", 최신.header.stamp.sec, "초")
for 초 in [0.5, 2.5]:
    try:
        버퍼.lookup_transform("base_link", "tip", Time(seconds=초))
    except ExtrapolationException as 오류:
        print(f"{초}초 →", str(오류).split(".")[0])
```

```text
1.00초의 손끝: (0.500, 0.000), 허리  0.0도
1.25초의 손끝: (0.462, 0.191), 허리 22.5도
1.50초의 손끝: (0.354, 0.354), 허리 45.0도
2.00초의 손끝: (0.000, 0.500), 허리 90.0도
Time()으로 물으면 가장 최근 것: 2 초
0.5초 → Lookup would require extrapolation into the past
2.5초 → Lookup would require extrapolation into the future
```

1초에 0도, 2초에 90도인 변환 두 개만 넣었는데, 1.25초와 1.5초를 물으니 22.5도와 45도가 나왔습니다. 두 시각 사이는 tf2가 **보간**해서 답해요. 회전은 2장 2.7절의 slerp로 잇기 때문에 손끝이 원 위를 따라갔습니다(1.5초에 (0.354, 0.354)). `Time()`(0초)으로 물으면 "가장 최근 것"을 달라는 뜻이라 2초의 변환이 왔어요.

가지고 있는 기록 밖은 답하지 않습니다. 0.5초는 기록보다 이르고(과거로 외삽), 2.5초는 기록보다 늦어서(미래로 외삽) 예외가 났어요. 실제 시스템에서 "방금 찍은 사진의 시각"으로 물었는데 관절 상태가 아직 도착하지 않았다면 이 미래 외삽 오류가 납니다. 그래서 tf2에 물을 때는 `timeout`을 주고 잠깐 기다리거나, 6.6절의 `관절_보내기`처럼 데이터가 들어온 것을 확인한 뒤 묻습니다.

### 자주 하는 실수

tf2와 `robot_state_publisher`에서 자주 만나는 실수 두 가지를 직접 일으켜 보겠습니다.

```python
import json
import subprocess
import tempfile

import numpy as np
from rclpy.duration import Duration
from rclpy.time import Time
from tf2_ros import TransformException

from tf도구 import 상태_발행기, 연결, 여기

# 실수 1: 뿌리 링크에 inertial을 적었다 → robot_state_publisher가 경고를 남긴다
urdf6 = subprocess.run(["xacro", str(여기 / "예제팔.urdf.xacro")], capture_output=True, text=True, check=True).stdout
with tempfile.NamedTemporaryFile("w", suffix=".yaml") as 파일:
    json.dump({"robot_state_publisher": {"ros__parameters": {"robot_description": urdf6}}}, 파일)
    파일.flush()
    결과 = subprocess.run(["timeout", "2", "ros2", "run", "robot_state_publisher", "robot_state_publisher",
                         "--ros-args", "--params-file", 파일.name], capture_output=True, text=True)
경고 = next(줄 for 줄 in 결과.stderr.splitlines() if "kdl_parser" in 줄)
print("실수 1:", 경고.split("]: ", 1)[1].split(".")[0])

# 실수 2: joint_states에 관절 하나를 빠뜨렸다 → 그 아래 좌표계는 tf에 나타나지 않는다
with 상태_발행기((여기 / "두관절팔.urdf").read_text()), 연결() as 팔:
    시각 = 팔.관절_보내기(["shoulder"], [0.5], 확인=("base_link", "upper_arm"))    # elbow를 빠뜨림
    print("실수 2: upper_arm까지는 됨 →", bool(팔.버퍼.can_transform("base_link", "upper_arm", 시각)))
    try:
        팔.버퍼.lookup_transform("base_link", "tip", Time(), timeout=Duration(seconds=1))
    except TransformException as 오류:          # tf2 조회 오류들의 공통 부모
        print("        tip은 →", type(오류).__name__)
        print("       ", str(오류).split(" because ")[1].split(".")[0])
```

```text
실수 1: The root link base_link has an inertia specified in the URDF, but KDL does not support a root link with an inertia
실수 2: upper_arm까지는 됨 → True
        tip은 → ConnectivityException
        they are not part of the same tree
```

첫째, 뿌리 링크(`base_link`)에 `inertial`을 적었더니 `robot_state_publisher`가 안에서 쓰는 기구학 라이브러리 KDL이 "관성을 가진 뿌리 링크는 지원하지 않는다"는 경고를 남겼습니다. tf 계산에는 지장이 없고 뿌리의 질량만 무시돼요. 질량 없는 빈 링크(흔히 `world`)를 뿌리로 하나 더 두고 `base_link`를 고정 관절로 붙이면 사라집니다.

둘째, `/joint_states`에 팔꿈치를 빠뜨렸습니다. `robot_state_publisher`는 각도를 모르는 관절의 변환을 지어내지 않아요. 그래서 `upper_arm`까지만 나무가 이어지고, `tip`은 `/tf_static`으로 `forearm`에만 붙은 떨어진 섬이 되어 tf2가 "같은 나무가 아니다"(`ConnectivityException`)라고 답했습니다. 관절 이름 하나만 틀려도 생기는 오류예요. tf2의 오류는 종류가 여럿이라 공통 부모인 `TransformException`으로 받는 것이 편합니다.

| 실수 | 증상 | 확인법 |
|---|---|---|
| `lookup_transform` 인자 순서를 바꿈 | 역변환이 나온다(위치가 그럴듯하게 틀린다) | "앞이 기준, 뒤가 대상", `T_A_B` = `("A", "B")` |
| `/joint_states`에 관절이 빠짐·이름 오타 | 그 아래 좌표계가 없다, `ConnectivityException` | `ros2 topic echo /joint_states`, 나무 출력 |
| 데이터보다 늦은 시각으로 물음 | `ExtrapolationException` | `timeout`을 주고 묻기, 시각 확인 |
| 뿌리 링크에 `inertial` | KDL 경고, 동역학에서 질량 무시 | 빈 뿌리 링크 하나 더 두기 |
| URDF를 명령줄 `-p`로 넘김 | xacro 결과에서 노드가 죽는다 | 파라미터 파일이나 launch의 `ParameterValue` |

## 6.8 시각화: RViz와 MuJoCo

### RViz

ROS에서 로봇을 눈으로 보는 표준 도구는 **RViz**(rviz2)입니다. URDF 모양, tf 좌표계, 카메라 영상, 레이저 점, 계획한 경로를 한 화면에 겹쳐 보여 줘요. RViz는 창을 띄우는 프로그램이라 이 책의 실행 환경(화면 없는 Docker)에서는 돌릴 수 없으니, 화면이 있는 리눅스 컴퓨터(또는 화면을 연결한 컨테이너)에서 쓰는 명령만 소개합니다.

```bash
# 6.6절의 launch 파일을 rviz 인자 없이 띄우면 RViz 창까지 열린다
ros2 launch ./팔보기.launch.py

# 관절을 슬라이더로 돌려 보려면 GUI판을 따로 설치해 joint_state_publisher 대신 띄운다
sudo apt install ros-lyrical-joint-state-publisher-gui
ros2 run joint_state_publisher_gui joint_state_publisher_gui

# 저장해 둔 화면 설정(.rviz)으로 열기
ros2 run rviz2 rviz2 -d 팔보기.rviz

# tf 나무를 PDF 그림으로 저장하기(graphviz 필요)
ros2 run tf2_tools view_frames
```

RViz 창이 열리면 세 가지를 설정합니다. 왼쪽 위 **Fixed Frame**을 `base_link`로 바꾸고(모든 것을 이 좌표계 기준으로 그린다), **Add** 버튼으로 **RobotModel**을 추가해 Description Topic을 `/robot_description`으로, 다시 **Add**로 **TF**를 추가해요. 그러면 URDF의 `visual` 모양과 좌표계 축들이 나타나고, 슬라이더를 움직이면 팔이 따라 움직입니다. 설정을 `File → Save Config`로 저장해 두면 다음부터 `-d` 옵션으로 바로 열 수 있어요.

### tf로 받은 좌표계를 그림으로

화면 없는 환경에서도 tf2가 알려 준 좌표계를 그림으로 그릴 수는 있습니다. 컨테이너 안에서 6자유도 팔의 모든 링크 좌표계를 tf2에 물어 파일로 저장하고, 내 컴퓨터에서 그 파일을 읽어 matplotlib으로 그리겠습니다.

```python
import subprocess

import numpy as np

from tf도구 import 상태_발행기, 연결, 여기

urdf = subprocess.run(["xacro", str(여기 / "예제팔.urdf.xacro")], capture_output=True, text=True, check=True).stdout
관절_이름 = [f"joint{i}" for i in range(1, 7)]
좌표계_이름 = ["base_link"] + [f"link{i}" for i in range(1, 7)] + ["tip"]

with 상태_발행기(urdf), 연결() as 팔:
    시각 = 팔.관절_보내기(관절_이름, np.deg2rad([30, 45, 60, 0, 45, 0]))
    행렬들 = np.array([팔.변환("base_link", 이름, 시각) for 이름 in 좌표계_이름])   # T_바닥_좌표계
np.save("arm6_tf.npy", 행렬들)                      # (8, 4, 4): 좌표계 8개의 4×4 변환
print("좌표계:", 좌표계_이름)
print("저장: arm6_tf.npy", 행렬들.shape)
```

```text
좌표계: ['base_link', 'link1', 'link2', 'link3', 'link4', 'link5', 'link6', 'tip']
저장: arm6_tf.npy (8, 4, 4)
```

좌표계 여덟 개의 4×4 변환을 `(8, 4, 4)` 배열 하나로 저장했습니다. 그림은 왼쪽에 tf 나무, 오른쪽에 좌표계 축들을 그려요. RViz의 TF 화면을 흉내 낸 것입니다.

```python
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

이름들 = ["base_link"] + [f"link{i}" for i in range(1, 7)] + ["tip"]
행렬들 = np.load("arm6_tf.npy")                     # 컨테이너에서 tf2로 받아 둔 T_바닥_좌표계

그림 = plt.figure(figsize=(9, 4.6))
칸들 = 그림.add_gridspec(1, 2, width_ratios=[1, 1.6])
# 왼쪽: tf 나무. 부모에서 자식으로 화살표, 관절 이름과 종류를 옆에 적는다
나무 = 그림.add_subplot(칸들[0])
for i, 이름 in enumerate(이름들):
    나무.text(0, -i, 이름, ha="center", va="center", fontsize=10,
            bbox=dict(boxstyle="round", fc="lightyellow" if 이름 != "tip" else "lavender"))
    if i > 0:
        나무.annotate("", xy=(0, -i + 0.3), xytext=(0, -i + 0.7), arrowprops=dict(arrowstyle="->"))
        설명 = "tip_joint (fixed → /tf_static)" if 이름 == "tip" else f"joint{i} (revolute → /tf)"
        나무.text(0.12, -i + 0.5, 설명, va="center", fontsize=8, color="dimgray")
나무.set_xlim(-0.4, 1.3)
나무.set_ylim(-len(이름들) + 0.4, 0.6)
나무.axis("off")
나무.set_title("tf 나무: 좌표계마다 부모가 하나", fontsize=10)

# 오른쪽: 각 좌표계의 원점과 축(x 빨강, y 초록, z 파랑)
칸 = 그림.add_subplot(칸들[1], projection="3d")
원점들 = 행렬들[:, :3, 3]
칸.plot(*원점들.T, "-", color="silver", linewidth=4)
for 이름, T in zip(이름들, 행렬들):
    for 열, 색 in zip(range(3), ["tab:red", "tab:green", "tab:blue"]):
        칸.plot(*zip(T[:3, 3], T[:3, 3] + 0.06 * T[:3, 열]), color=색, linewidth=1.5)
for 이름 in ["base_link", "link3", "tip"]:
    칸.text(*(행렬들[이름들.index(이름)][:3, 3] + [0.02, 0.02, 0.03]), 이름, fontsize=8)
칸.set_xlim(-0.1, 0.5)
칸.set_ylim(-0.1, 0.5)
칸.set_zlim(0, 0.6)
칸.set_box_aspect((1, 1, 1))
칸.set_xticks([0, 0.2, 0.4])
칸.set_yticks([0, 0.2, 0.4])
칸.set_xlabel("x (m)")
칸.set_ylabel("y (m)")
칸.set_zlabel("z (m)")
칸.view_init(elev=20, azim=-60)
칸.set_title("tf2로 받은 좌표계들 (30, 45, 60, 0, 45, 0)도", fontsize=10)
그림.tight_layout()
그림.savefig("tf_tree.png", dpi=200)
print("저장: tf_tree.png")
```

```text
저장: tf_tree.png
```

![왼쪽은 예제 팔의 tf 나무로 base_link에서 tip까지 여덟 좌표계가 한 줄로 이어지고, joint1~6은 /tf, tip_joint는 /tf_static으로 온다. 오른쪽은 tf2로 받은 좌표계 여덟 개의 원점과 x(빨강), y(초록), z(파랑) 축을 3차원으로 그린 것으로, 3장의 6자유도 팔 그림과 같은 자세다.](../assets/images/ch06/tf_tree.png)

오른쪽 그림은 3장 3.3절에서 순기구학으로 그린 팔과 같은 자세입니다. 좌표계마다 파란 z축을 보면, 관절이 0도인 축 방향을 따라 링크가 뻗어 있어요. 이 팔의 링크가 모두 자기 z축 방향으로 뻗도록 만들었기 때문입니다. 손끝 근처에 좌표계가 촘촘히 모인 것은 손목 관절 세 개가 5cm 간격으로 붙어 있어서예요.

### MuJoCo로 그리기

6.3절에서 MuJoCo가 URDF를 바로 읽는 것을 봤으니, MuJoCo로 그림자까지 있는 그림도 그릴 수 있습니다. 다만 URDF에는 바닥도 조명도 없어요. 로봇만 적는 파일이니까요. 이럴 때는 URDF를 `mujoco.MjSpec`으로 읽으면 됩니다. `MjSpec`은 MuJoCo 모델의 **고칠 수 있는 설계도**라서, 읽어 들인 뒤 바닥·조명·손끝 표시점(`site`)을 코드로 덧붙이고 `compile()`로 모델을 만들 수 있어요.

```python
import mujoco
import numpy as np
from PIL import Image

from 팔URDF import URDF

# URDF를 MjSpec(고칠 수 있는 모델 설계도)으로 읽고, URDF에 없는 바닥·조명·색을 덧붙인다
설계 = mujoco.MjSpec.from_string(URDF())
설계.worldbody.add_light(pos=[0, -1, 2], dir=[0, 0.5, -1])
설계.worldbody.add_geom(type=mujoco.mjtGeom.mjGEOM_PLANE, size=[1, 1, 0.1], rgba=[0.9, 0.9, 0.9, 1])
for 모양 in 설계.geoms:
    if 모양.type == mujoco.mjtGeom.mjGEOM_CYLINDER:
        모양.rgba = [0.8, 0.5, 0.2, 1]
설계.body("link6").add_site(name="tip", pos=[0, 0, 0.05], size=[0.015, 0, 0], rgba=[0.1, 0.3, 0.9, 1])
설계.worldbody.add_geom(type=mujoco.mjtGeom.mjGEOM_SPHERE, size=[0.02, 0, 0], pos=[0.484, -0.155, 0.09],
                       rgba=[0.9, 0.1, 0.1, 1])                # 6.7절에서 손목 카메라가 본 컵
모델 = 설계.compile()
데이터 = mujoco.MjData(모델)

카메라 = mujoco.MjvCamera()
카메라.lookat[:] = [0.25, 0.0, 0.25]
카메라.distance, 카메라.azimuth, 카메라.elevation = 1.3, -100, -20
사진들 = []
with mujoco.Renderer(모델, 400, 400) as 그리개:
    for 관절각_도 in [[30, 45, 60, 0, 45, 0], [-20, 30, 70, 0, 60, 0]]:
        데이터.qpos[:] = np.deg2rad(관절각_도)
        mujoco.mj_forward(모델, 데이터)
        그리개.update_scene(데이터, camera=카메라)
        사진들.append(그리개.render())
        print(f"{관절각_도} → 손끝 {np.round(데이터.site('tip').xpos, 3) + 0.0}")
Image.fromarray(np.hstack(사진들)).save("arm6_urdf_mujoco.png")
print("저장: arm6_urdf_mujoco.png")
```

```text
[30, 45, 60, 0, 45, 0] → 손끝 [0.478 0.276 0.248]
[-20, 30, 70, 0, 60, 0] → 손끝 [ 0.451 -0.164  0.314]
저장: arm6_urdf_mujoco.png
```

![MuJoCo가 URDF를 읽어 그린 6자유도 예제 팔. 왼쪽은 관절 (30, 45, 60, 0, 45, 0)도, 오른쪽은 (-20, 30, 70, 0, 60, 0)도 자세다. 빨간 공은 6.7절에서 손목 카메라가 본 컵의 위치로, 오른쪽 자세에서 손끝 앞 아래쪽에 있다.](../assets/images/ch06/arm6_urdf_mujoco.png)

왼쪽 자세의 손끝은 3장과 같은 (0.478, 0.276, 0.248)입니다. 빨간 공은 6.7절에서 손목 카메라가 두 번째 자세로 본 컵의 위치 (0.484, -0.155, 0.09)예요. 오른쪽 그림에서 손끝이 아래를 향한 채 컵을 내려다보고 있죠. 왼쪽 자세에서는 컵이 팔 뒤쪽에 가려 조금만 보입니다.

함정이 하나 있었습니다. 처음에 컵 공을 "부딪히지 않는 모양"(`contype=0, conaffinity=0`)으로 만들었더니 그림에서 사라졌어요. URDF에서 시작한 모델은 `discardvisual`이 켜져 있어서, 부딪히지 않는 모양을 "보이기만 하는 모양"으로 여겨 버리기 때문입니다.

## 6.9 SO-101 팔의 URDF 둘러보기

1장에서 이 책은 저가 로봇 팔 키트를 7장과 21장에서 다룬다고 했습니다. 이 책이 고른 키트는 **SO-101**이에요. RobotStudio가 Hugging Face와 함께 설계한 오픈 소스 팔로, 3D 프린터로 뽑은 부품에 Feetech STS3215 서보 여섯 개를 달고, Hugging Face의 로봇 학습 라이브러리 LeRobot과 함께 쓰도록 만들어졌어요. 설계 파일은 GitHub의 `TheRobotStudio/SO-ARM100` 저장소에 Apache-2.0 라이선스로 공개되어 있고, `Simulation/SO101` 폴더에 URDF(`so101_new_calib.urdf` 등)와 MuJoCo용 MJCF(`so101_new_calib.xml`), 메시 파일(`assets/` 아래 STL)이 들어 있습니다. 이 책의 저장소에는 남의 파일을 복사해 두지 않았으니, 직접 보려면 그 저장소에서 내려받으세요. 이 장에서 배운 눈으로 구조만 읽어 보겠습니다.

| 관절 | 종류 | 부모 → 자식 | 범위(도) |
|---|---|---|---|
| `shoulder_pan` | revolute | `base_link` → `shoulder_link` | -110 ~ 110 |
| `shoulder_lift` | revolute | `shoulder_link` → `upper_arm_link` | -100 ~ 100 |
| `elbow_flex` | revolute | `upper_arm_link` → `lower_arm_link` | -96.8 ~ 96.8 |
| `wrist_flex` | revolute | `lower_arm_link` → `wrist_link` | -95 ~ 95 |
| `wrist_roll` | revolute | `wrist_link` → `gripper_link` | -157.2 ~ 162.8 |
| `gripper` | revolute | `gripper_link` → `moving_jaw_so101_v1_link` | -10 ~ 100 |
| `gripper_frame_joint` | fixed | `gripper_link` → `gripper_frame_link` | 없음 |

이 장의 지식으로 읽을 수 있는 점이 여럿 있습니다.

- **사슬 다섯 관절 + 집게 하나**: 허리(pan), 어깨(lift), 팔꿈치(flex), 손목 굽힘(flex), 손목 돌림(roll)으로 5자유도이고, 여섯째 서보가 집게 턱 하나를 여닫습니다. 3장의 예제 팔보다 하나 적어서 손끝의 자세를 마음대로 정할 수는 없어요(3장 3.1절의 자유도 이야기)
- **`gripper_frame_link`는 빈 링크**입니다. 이 장의 `tip`처럼, 집게 끝에 "손끝 좌표계"를 붙이려고 고정 관절로 단 링크예요. 역기구학의 목표는 보통 이 좌표계로 잡습니다
- **모든 관절의 `axis`가 `0 0 1`(z축)** 이고, 대신 `origin`의 `rpy`가 0이 아닙니다. 예를 들어 `shoulder_pan`은 `rpy="3.14159 4.18253e-17 -3.14159"`예요. 6.4절에서 말한 "축은 z로 두고 관절 좌표계를 rpy로 돌려 놓는" 방식입니다. 파일 맨 위에 `Generated using onshape-to-robot`이라는 주석이 있는데, CAD 프로그램 Onshape의 설계에서 이 도구로 URDF를 뽑아낸 것이에요. 이런 도구들은 관절 축을 z로 맞추는 경우가 많습니다
- **visual과 collision이 같은 STL 메시**를 씁니다. 링크마다 3D 프린터 부품과 서보 모양을 여러 개 붙였어요. 단순한 모양 대신 실제 부품 모양으로 충돌을 계산하니 정확하지만 계산은 무겁습니다
- **링크마다 `inertial`** 이 있고, 집게 턱과 빈 링크를 빼면 질량은 0.08~0.15kg 정도입니다. CAD에서 계산한 값이에요. `base_link`에도 질량이 있으니, `robot_state_publisher`로 띄우면 6.7절에서 본 KDL 경고가 나올 겁니다

저장소 설명에 따르면 "새 보정(new calib)" 파일은 각 관절의 0도를 **움직이는 범위의 한가운데**로, "옛 보정(old calib)" 파일은 팔을 수평으로 쭉 편 자세를 0도로 잡았습니다. 같은 팔이라도 "0도가 어떤 자세인가"가 파일마다 다를 수 있다는 뜻이에요. 3장 Q&A에서 말한 "도구마다 다른 약속"의 실제 예입니다.

## 6.10 실습: 3관절 팔로 손끝 궤적 기록하기

### 무엇을 만드나

이 장에서 배운 것을 모아 작은 팔 하나를 처음부터 만들어 보겠습니다. SO-101의 앞쪽 세 관절처럼 생긴 3관절 팔이에요. 허리(`pan`, z축)가 방향을 돌리고, 어깨(`lift`)와 팔꿈치(`elbow`, 둘 다 y축)가 세로 평면에서 팔을 굽힙니다. 이 팔의 손끝으로 바닥 위 5cm 높이에 원을 그리게 할 거예요. 순서는 이렇습니다.

1. xacro로 팔을 적는다. 위팔·아래팔 길이는 명령줄 인자로 바꿀 수 있게 한다
2. 원 위의 점마다 관절 각도를 계산한다(역기구학)
3. 각도를 `/joint_states`로 차례로 발행하고, `robot_state_publisher`가 만든 tf에서 손끝 위치를 기록한다
4. 기록을 파일로 저장하고, 내 컴퓨터에서 그림으로 그린다

### xacro로 팔 적기

다음 내용을 `세관절팔.urdf.xacro`로 저장하세요. 6.5절의 `rod_link` 매크로를 질량을 받도록 고쳤고, 관절도 `hinge` 매크로로 만들었습니다.

```xml
<?xml version="1.0"?>
<!-- 6.10절 실습: 허리(z) + 어깨(y) + 팔꿈치(y) 3관절 팔. 링크 길이는 명령줄에서 바꿀 수 있다 -->
<robot name="arm3" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <xacro:arg name="upper" default="0.20"/>                <!-- 위팔 길이(m) -->
  <xacro:arg name="fore" default="0.18"/>                 <!-- 아래팔 길이(m) -->
  <xacro:property name="radius" value="0.015"/>

  <xacro:macro name="rod_link" params="name length mass">
    <link name="${name}">
      <visual>
        <origin xyz="0 0 ${length / 2}"/>
        <geometry><cylinder radius="${radius}" length="${length}"/></geometry>
      </visual>
      <collision>
        <origin xyz="0 0 ${length / 2}"/>
        <geometry><cylinder radius="${radius}" length="${length}"/></geometry>
      </collision>
      <inertial>
        <origin xyz="0 0 ${length / 2}"/>
        <mass value="${mass}"/>
        <inertia ixx="${mass * (3 * radius**2 + length**2) / 12}" ixy="0" ixz="0"
                 iyy="${mass * (3 * radius**2 + length**2) / 12}" iyz="0" izz="${mass * radius**2 / 2}"/>
      </inertial>
    </link>
  </xacro:macro>

  <xacro:macro name="hinge" params="name parent child z axis lower upper">
    <joint name="${name}" type="revolute">
      <parent link="${parent}"/>
      <child link="${child}"/>
      <origin xyz="0 0 ${z}"/>
      <axis xyz="${axis}"/>
      <limit lower="${lower}" upper="${upper}" effort="3" velocity="3"/>
    </joint>
  </xacro:macro>

  <xacro:rod_link name="base_link" length="0.05" mass="0.3"/>
  <xacro:hinge name="pan" parent="base_link" child="shoulder_link" z="0.05" axis="0 0 1"
               lower="${-pi}" upper="${pi}"/>
  <xacro:rod_link name="shoulder_link" length="0.05" mass="0.1"/>
  <xacro:hinge name="lift" parent="shoulder_link" child="upper_arm" z="0.05" axis="0 1 0"
               lower="${-pi / 2}" upper="${pi / 2}"/>
  <xacro:rod_link name="upper_arm" length="$(arg upper)" mass="0.15"/>
  <xacro:hinge name="elbow" parent="upper_arm" child="forearm" z="$(arg upper)" axis="0 1 0"
               lower="${-2.6}" upper="${2.6}"/>
  <xacro:rod_link name="forearm" length="$(arg fore)" mass="0.1"/>

  <joint name="tip_joint" type="fixed">
    <parent link="forearm"/>
    <child link="tip"/>
    <origin xyz="0 0 $(arg fore)"/>
  </joint>
  <link name="tip"/>
</robot>
```

관절 범위도 매크로 인자로 받게 해서 어깨는 ±90도, 팔꿈치는 ±2.6rad(약 ±149도)로 정했어요. 어깨(`lift`) 축은 바닥에서 0.1m(받침 0.05m + 어깨 링크 0.05m) 위에 있습니다.

### 각도를 보내고 tf로 기록하기

역기구학은 3장 3.4절의 2링크 공식을 그대로 씁니다. 허리 각도는 목표 점의 방향(`arctan2(y, x)`)으로 정하고, 남은 세로 평면에서 어깨와 팔꿈치를 2링크 팔처럼 풀어요. 이 팔은 똑바로 선 자세가 0도라서, 2링크 공식의 x 자리에 세로 거리를, y 자리에 가로 거리를 넣는 것만 다릅니다. 링크 길이는 숫자로 다시 적지 않고 xacro가 펼친 URDF에서 읽었어요. 명령줄 인자로 길이를 바꿔도 역기구학이 따라가게 하려는 것입니다.

```python
import subprocess

import numpy as np
from urdf_parser_py.urdf import URDF

from tf도구 import 상태_발행기, 연결, 여기
from urdf기구학 import URDF_순기구학

urdf = subprocess.run(["xacro", str(여기 / "세관절팔.urdf.xacro")], capture_output=True, text=True, check=True).stdout
로봇 = URDF.from_xml_string(urdf)
L1 = 로봇.joint_map["elbow"].origin.xyz[2]           # 위팔 길이: URDF에서 읽는다
L2 = 로봇.joint_map["tip_joint"].origin.xyz[2]       # 아래팔 길이
어깨_높이 = 0.1                                     # 바닥에서 어깨(lift) 축까지


def 역기구학(목표: np.ndarray) -> np.ndarray:
    """손끝 목표 (x, y, z) → (pan, lift, elbow). 허리로 방향을 맞추고, 남은 세로 평면은 3장 3.4절의 2링크 공식."""
    pan = np.arctan2(목표[1], 목표[0])
    가로, 세로 = np.hypot(목표[0], 목표[1]), 목표[2] - 어깨_높이
    # 이 팔은 위(z)를 0도로 재므로 2링크 공식의 x 자리에 세로, y 자리에 가로를 넣는다
    c = (가로**2 + 세로**2 - L1**2 - L2**2) / (2 * L1 * L2)
    elbow = np.arccos(np.clip(c, -1, 1))
    lift = np.arctan2(가로, 세로) - np.arctan2(L2 * np.sin(elbow), L1 + L2 * np.cos(elbow))
    return np.array([pan, lift, elbow])


# 손끝으로 그릴 원: 바닥 위 5cm 높이, 중심 (0.22, 0), 반지름 0.08m, 72점
각 = np.linspace(0, 2 * np.pi, 73)
목표들 = np.column_stack([0.22 + 0.08 * np.cos(각), 0.08 * np.sin(각), np.full_like(각, 0.05)])
관절_이름 = ["pan", "lift", "elbow"]
좌표계_이름 = ["base_link", "shoulder_link", "upper_arm", "forearm", "tip"]

기록 = []
with 상태_발행기(urdf), 연결() as 팔:
    for 목표 in 목표들:
        q = 역기구학(목표)
        시각 = 팔.관절_보내기(관절_이름, q)                          # 관절 각도를 발행하고
        원점들 = [팔.변환("base_link", 이름, 시각)[:3, 3] for 이름 in 좌표계_이름]   # tf로 확인
        기록.append(np.concatenate([q, np.ravel(원점들)]))
기록 = np.array(기록)
손끝_tf = 기록[:, -3:]

직접 = np.array([URDF_순기구학(로봇, dict(zip(관절_이름, 행[:3])), "tip")[:3, 3] for 행 in 기록])
print(f"위팔 {L1}m, 아래팔 {L2}m / 점 {len(목표들)}개를 발행하고 tf로 손끝을 기록")
print(f"tf 손끝과 목표 원의 최대 차이     : {np.abs(손끝_tf - 목표들).max():.1e} m")
print(f"tf 손끝과 URDF 순기구학의 최대 차이: {np.abs(손끝_tf - 직접).max():.1e} m")
범위 = np.rad2deg([기록[:, 0].min(), 기록[:, 0].max()]).round(1)
print(f"허리 pan의 범위: {범위[0]}~{범위[1]}도")
np.savetxt("trace.csv", 기록, delimiter=",", fmt="%.6f",
           header="pan,lift,elbow," + ",".join(f"{이름}_{축}" for 이름 in 좌표계_이름 for 축 in "xyz"))
print("저장: trace.csv")
```

```text
위팔 0.2m, 아래팔 0.18m / 점 73개를 발행하고 tf로 손끝을 기록
tf 손끝과 목표 원의 최대 차이     : 1.7e-16 m
tf 손끝과 URDF 순기구학의 최대 차이: 2.2e-16 m
허리 pan의 범위: -21.3~21.3도
저장: trace.csv
```

원 위의 점 73개(처음과 끝이 같은 점)마다 관절 각도를 발행하고, 그 시각의 tf에서 손끝과 각 좌표계의 원점을 기록했습니다. tf가 알려 준 손끝은 목표 원과 1.7e-16m, URDF로 직접 계산한 순기구학과 2.2e-16m 차이로 같아요. 역기구학, URDF, `robot_state_publisher`, tf2가 한 줄로 맞물려 돌았다는 뜻입니다. 허리는 원의 양쪽 끝을 향해 -21.3도에서 21.3도 사이를 오갔어요. 기록은 `trace.csv`에 관절 각도 셋과 좌표계 다섯 개의 원점(x, y, z)을 한 줄씩 저장했습니다.

### 그림으로 그리기

```python
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

기록 = np.loadtxt("trace.csv", delimiter=",")          # 컨테이너가 tf로 기록한 값
관절각 = np.rad2deg(기록[:, :3])
원점들 = 기록[:, 3:].reshape(len(기록), 5, 3)            # 걸음마다 좌표계 5개의 원점
손끝 = 원점들[:, -1]

그림 = plt.figure(figsize=(10, 3.8))
칸 = 그림.add_subplot(1, 3, 1, projection="3d")
for k in range(0, len(기록), 12):                        # 몇 걸음만 팔 모양을 그린다
    칸.plot(*원점들[k].T, "o-", color="dimgray", alpha=0.5, markersize=2)
칸.plot(*손끝.T, color="tab:red", linewidth=2)
칸.set_xlim(0, 0.3)
칸.set_ylim(-0.15, 0.15)
칸.set_zlim(0, 0.3)
칸.set_box_aspect((1, 1, 1))
칸.set_xticks([0, 0.1, 0.2, 0.3])
칸.set_yticks([-0.1, 0, 0.1])
칸.view_init(elev=25, azim=-130)
칸.set_title("팔과 손끝 궤적", fontsize=10)

위 = 그림.add_subplot(1, 3, 2)
위.plot(손끝[:, 0], 손끝[:, 1], color="tab:red")
위.plot(0, 0, "ks")
위.set_aspect("equal")
위.set_xlabel("x (m)")
위.set_ylabel("y (m)")
위.set_title("위에서 본 손끝(높이 0.05m)", fontsize=10)

관절 = 그림.add_subplot(1, 3, 3)
for i, 이름 in enumerate(["pan", "lift", "elbow"]):
    관절.plot(관절각[:, i], label=이름)
관절.set_xlabel("걸음")
관절.set_ylabel("관절 각도(도)")
관절.legend(fontsize=8)
관절.set_title("발행한 관절 각도", fontsize=10)
그림.tight_layout()
그림.savefig("trace.png", dpi=200)
print("저장: trace.png")
```

```text
저장: trace.png
```

![3관절 팔의 손끝 궤적. 왼쪽은 몇 걸음의 팔 모양(회색)과 손끝이 그린 원(빨강)을 3차원으로, 가운데는 위에서 본 손끝 궤적으로 중심 (0.22, 0), 반지름 0.08m의 원이다. 오른쪽은 걸음마다 발행한 pan, lift, elbow 각도로, 손끝이 팔에서 멀어질수록 팔꿈치가 펴지고 가까워질수록 굽는다.](../assets/images/ch06/trace.png)

가운데 그림에서 손끝이 정확한 원을 그렸습니다. 검은 네모가 팔의 받침이에요. 오른쪽의 관절 각도를 보면 원을 그리는 데 세 관절이 모두 꽤 복잡하게 움직였습니다. 손끝이 받침에서 가장 가까운 점(0.14m)을 지날 때(걸음 36 근처) 팔꿈치가 가장 크게 굽었고(134도쯤), 가장 먼 점(0.30m)에서 가장 펴졌어요. 허리는 원의 위쪽 절반에서 왼쪽(+), 아래쪽 절반에서 오른쪽(-)으로 돌았습니다. 손끝으로는 단순한 원인데 관절 공간에서는 이렇게 생긴 곡선이에요. 3장 3.1절에서 말한 관절 공간과 작업 공간의 차이를 다시 한 번 눈으로 본 셈입니다.

더 해 보고 싶다면 xacro를 펼치는 줄에 `upper:=0.25`, `fore:=0.15` 같은 인자를 넣어 링크 길이를 바꿔 보세요. 역기구학이 URDF에서 길이를 읽으니 다른 코드는 고칠 필요가 없습니다. 원의 반지름을 0.15m로 키워 팔이 닿지 않는 점을 만들어 보는 것도 좋아요. `np.clip`이 어떤 각도를 만들고, tf의 손끝이 목표에서 얼마나 벗어나는지 확인할 수 있습니다.

## 6.11 정리와 다음 장 미리보기

이 장에서 로봇의 몸을 모두가 읽는 한 장의 설계도로 적었습니다.

- **URDF**: `<robot>` 안의 `<link>`와 `<joint>`. 관절은 부모 하나와 자식 하나를 잇고, 로봇은 뿌리가 하나인 나무 모양이다. 관절 종류는 revolute(범위 있는 회전), continuous(끝없는 회전), prismatic(직선), fixed(고정). `axis`의 기본값은 x축. 고치면 `check_urdf`부터
- **origin과 rpy**: 자식 좌표계는 부모 기준 `origin xyz rpy`에 있다. rpy는 고정 축 롤 → 피치 → 요, 곧 `Rz @ Ry @ Rx`(SciPy 소문자 `"xyz"`). `static_transform_publisher`도 같고, MuJoCo의 `euler`(대문자 `"XYZ"`)와는 다르다
- **링크의 세 얼굴**: visual은 보이는 모양, collision은 부딪히는 단순한 모양, inertial은 질량·무게중심·관성. inertial이 틀리면 모양은 같아도 시뮬레이션의 움직임이 틀린다. MuJoCo는 inertial이 없으면 물의 밀도로 질량을 지어낸다
- **MuJoCo와 URDF**: MuJoCo는 URDF를 바로 읽는다. 기본으로 visual을 버리고 고정된 몸체를 합친다(`discardvisual`, `fusestatic`). `MjSpec`으로 읽으면 바닥·조명을 덧붙일 수 있다
- **xacro**: `property`(상수), `macro`(덩어리), `arg`(명령줄 인자), `${식}`. `.xacro`를 고치고 `xacro`로 펼친다
- **robot_state_publisher**: URDF와 `/joint_states`를 받아 움직이는 관절은 `/tf`, 고정 관절은 `/tf_static`으로 보낸다. joint_state_publisher는 연습용 관절 각도를 보낸다. launch 파일에서는 `Command`와 `ParameterValue(value_type=str)`로 xacro 결과를 넘긴다
- **tf2**: 좌표계 나무, 시각과 함께 쌓아 두는 버퍼, 두 시각 사이 보간과 외삽 오류. `T_A_B` = `lookup_transform("A", "B")` = `tf2_echo A B`, "앞이 기준, 뒤가 대상"
- **검산**: 3장의 순기구학, URDF 순기구학, tf2, MuJoCo가 모두 같은 손끝 위치를 냈다

이 장의 팔은 아직 소프트웨어 속에만 있습니다. `/joint_states`의 각도는 우리가 지어낸 숫자였고, 손끝은 tf2 버퍼 안에서만 움직였어요. 다음 7장에서는 이 숫자 뒤에 있는 진짜 부품을 만납니다. 관절을 돌리는 서보 모터와 세상을 재는 센서, 컴퓨터와 부품이 한 글자씩 주고받는 직렬 통신, 그리고 로봇의 두뇌 역할을 하는 라즈베리파이와 Jetson이에요. 실물 서보가 알려 주는 각도를 `/joint_states`로 내보내기만 하면, 이 장의 `robot_state_publisher`와 tf2는 아무것도 고치지 않고 그 팔의 좌표계 나무를 그려 줍니다. 지어낸 숫자를 진짜 숫자로 바꾸는 것, 그것이 7장의 일입니다.
