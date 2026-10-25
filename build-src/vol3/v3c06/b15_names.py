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
