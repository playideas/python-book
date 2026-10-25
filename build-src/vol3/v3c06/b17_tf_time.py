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
