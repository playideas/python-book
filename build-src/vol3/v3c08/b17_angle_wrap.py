import numpy as np

from 바퀴로봇 import 각도_감싸기, 표지_R, 표지_야코비안, 표지_보기

# 로봇은 (0, 0)에서 동쪽을 보고, 표지는 거의 바로 뒤에 있다
x = np.array([0.0, 0.0, 0.0])
P = np.diag([0.05**2, 0.05**2, np.deg2rad(3.0) ** 2])
표지 = np.array([-2.0, 0.03])
예상 = 표지_보기(x, 표지)
z = np.array([2.0, np.deg2rad(-179.5)])              # 센서는 -180~180도로 알려 준다
print(f"예상한 방향 {np.rad2deg(예상[1]):+.1f}도, 잰 방향 {np.rad2deg(z[1]):+.1f}도")

H = 표지_야코비안(x, 표지)
K = P @ H.T @ np.linalg.inv(H @ P @ H.T + 표지_R)
for 감싸기 in [False, True]:
    혁신 = z - 예상
    if 감싸기:
        혁신[1] = 각도_감싸기(혁신[1])
    새_x = x + K @ 혁신
    print(f"감싸기 {'O' if 감싸기 else 'X'}: 방향 혁신 {np.rad2deg(혁신[1]):+7.1f}도 → 고친 방향 "
          f"{np.rad2deg(각도_감싸기(새_x[2])):+7.1f}도, 위치 ({새_x[0]:+.2f}, {새_x[1]:+.2f})m")
