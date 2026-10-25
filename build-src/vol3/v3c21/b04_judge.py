import mujoco

from 손배치 import 손_배치
from 작업판단 import 고르기
from 책상인지 import 물건_찾기
from 책상장면 import 대기_자세, 상자들, 장면_xml, 찍기

모델 = mujoco.MjModel.from_xml_string(장면_xml(손_배치))
데이터 = mujoco.MjData(모델)
데이터.qpos[:6] = 데이터.ctrl[:6] = 대기_자세
mujoco.mj_forward(모델, 데이터)
물건들 = 물건_찾기(*찍기(모델, 데이터))


def 지시_종류(지시: str) -> tuple[str, ...]:
    """'빨간 것만'처럼 '만'이 붙은 색만 고른다. 그 밖의 말은 모든 종류(19장 규칙 계획기의 아주 작은 판)."""
    색_말 = {"빨간": "빨강", "초록": "초록", "파란": "파랑"}
    고른 = tuple(종류 for 말, 종류 in 색_말.items() if 말 in 지시)
    return 고른 if 고른 and "만" in 지시 else tuple(상자들)


for 지시 in ["책상 좀 치워 줘", "빨간 것만 치워 줘", "초록 블록만 정리해"]:
    대상, 건너뜀 = 고르기(물건들, 지시_종류(지시), 실패_자리=[])
    다음 = f"{대상['종류']}({대상['중심'][0]:.2f}, {대상['중심'][1]:.2f})" if 대상 else "없음"
    print(f"[{지시}] 할 종류 {지시_종류(지시)} → 다음 대상: {다음}")
    for 글 in 건너뜀:
        print("   건너뜀:", 글)
