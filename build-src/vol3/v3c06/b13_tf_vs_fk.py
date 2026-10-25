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
