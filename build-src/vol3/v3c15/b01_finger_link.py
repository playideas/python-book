from 집게시험장면 import 만들기, 흘려보내기

# 상자는 옆(y = 0.2m)으로 치워 두고, 공중에서 손가락만 움직여 본다
for 묶기 in [True, False]:
    모델, 데이터 = 만들기(상자_y=0.2, 묶기=묶기)
    데이터.joint("finger_l").qpos = 0.04                   # 일부러 짝짝이로 시작: 왼쪽은 활짝, 오른쪽은 1cm
    데이터.joint("finger_r").qpos = 0.01
    print("equality로 묶음" if 묶기 else "묶지 않음")
    for 너비 in [0.06, 0.03]:
        데이터.ctrl[모델.actuator("grip").id] = 너비          # 명령은 손가락 사이 너비(m) 하나
        흘려보내기(모델, 데이터, 1.0)
        왼, 오 = 데이터.joint("finger_l").qpos[0], 데이터.joint("finger_r").qpos[0]
        print(f"  너비 명령 {너비 * 100:.0f}cm → 왼쪽 {왼 * 100:.2f}cm, 오른쪽 {오 * 100:.2f}cm, "
              f"잰 너비 {데이터.sensor('width').data[0] * 100:.2f}cm, 쥐는 가운데가 {abs(왼 - 오) / 2 * 100:.2f}cm 틀어짐")
