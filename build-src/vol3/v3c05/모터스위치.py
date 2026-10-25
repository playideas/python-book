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
