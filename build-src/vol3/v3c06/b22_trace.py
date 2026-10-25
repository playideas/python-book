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
