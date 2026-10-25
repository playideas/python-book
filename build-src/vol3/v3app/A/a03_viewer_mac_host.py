"""맥에서 launch_passive를 python으로 부르면 어떻게 되는지 확인한다(창은 열리지 않는다)."""
import platform

import mujoco
import mujoco.viewer

모델 = mujoco.MjModel.from_xml_string("<mujoco/>")
데이터 = mujoco.MjData(모델)
print("운영체제:", platform.system())
try:
    mujoco.viewer.launch_passive(모델, 데이터)
except RuntimeError as 오류:
    print("RuntimeError:", 오류)
