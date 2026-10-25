"""21장 21.7절: 무작위 배치 여러 판으로 정리 로봇을 평가하고, 실패 원인을 기록에서 모은다."""
import re
from collections import Counter

import mujoco
import numpy as np

from 책상인지 import 어느_상자
from 책상장면 import 무작위_배치, 물성, 상자들, 장면_xml
from 정리로봇 import 정리로봇

# 정답지: '현실 역할' 책상(20장처럼 봉투에 넣어 둔 셈 친다). 마찰·무게·조명·깊이 잡음·카메라 받침이 다르다
현실_물성 = 물성(물건_마찰=0.3, 패드_마찰=0.6, 질량_배율=2.0, 밝기=0.6, 깊이_잡음=0.002, 카메라_틀어짐=(0.02, 0.015, 0.0))


def 한_판(씨앗: int, p: 물성 = 물성(), 보정=(0.0, 0.0, 0.0)) -> dict:
    """빨강 둘, 초록 둘, 파랑 하나를 무작위로 놓고 정리시킨 뒤 시뮬레이터가 아는 정답으로 채점한다."""
    물건들 = 무작위_배치(np.random.default_rng(씨앗), {"빨강": 2, "초록": 2, "파랑": 1})
    모델 = mujoco.MjModel.from_xml_string(장면_xml(물건들, p))
    데이터 = mujoco.MjData(모델)
    기록 = 정리로봇(모델, 데이터, p, 씨앗=씨앗, 카메라_보정=보정).정리()
    파랑 = next(물건 for 물건 in 물건들 if 물건["종류"] == "파랑")
    return {"정리": sum(어느_상자(데이터.body(물건["이름"]).xpos) == 물건["종류"] for 물건 in 물건들 if 물건["종류"] in 상자들),
            "시간": 데이터.time,
            "원인": Counter(re.sub(r"\(.*?\)", "", 메모.split(") ", 1)[-1]) for _, 무엇, 메모 in 기록 if 무엇 == "실패"),
            "확인 실패": sum(무엇 == "확인 실패" for _, 무엇, _ in 기록),
            "파랑 건드림": np.linalg.norm(데이터.body(파랑["이름"]).xpos[:2] - 파랑["위치"]) > 0.005}


def 요약(이름: str, 판들: list[dict]) -> str:
    원인 = sum((판["원인"] for 판 in 판들), Counter())
    return (f"{이름}: 다 정리한 판 {sum(판['정리'] == 4 for 판 in 판들)}/{len(판들)}, "
            f"물건 {sum(판['정리'] for 판 in 판들)}/{4 * len(판들)}, 판당 {np.mean([판['시간'] for 판 in 판들]):.1f}초, "
            f"실패 {sum(원인.values())}번 {dict(원인.most_common())}, 확인 실패 {sum(판['확인 실패'] for 판 in 판들)}번, "
            f"파랑 건드림 {sum(판['파랑 건드림'] for 판 in 판들)}판")
