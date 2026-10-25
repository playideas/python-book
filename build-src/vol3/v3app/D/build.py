"""terms.py와 찾은 장 번호로 부록 D 원고를 만든다."""
import json, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from terms import KO, EN
여기 = Path(__file__).parent
찾음 = json.load(open(여기 / "found.json"))
장 = {k: (b if b is not None else a) for k, (a, b) in 찾음.items()}
# 굵게 쓴 첫 자리가 예고(다음 장 미리보기 등)이거나 굵게 쓰지 않은 용어는 실제로 설명한 장으로 고친다
고침 = {"칼만 필터": 8, "자세": 2, "SLAM": 11, "PID 제어": 12, "강화 학습": 17, "모방 학습": 18,
        "계획": 19, "ROS 2": 5, "URDF": 6, "패킷": 7, "계산 토크 제어": 12, "기술": 19, "A*": 13,
        "MuJoCo": 1, "sim2real": 20}
장.update(고침)
# 한글 목록에 넣었지만 영문(약자)으로 시작하는 용어는 D.2로 옮긴다
KO, EN = [r for r in KO if not r[0][0].isascii() or r[0][0].isdigit()], EN + [r for r in KO if r[0][0].isascii() and not r[0][0].isdigit()]
초성 = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
기본 = {"ㄲ": "ㄱ", "ㄸ": "ㄷ", "ㅃ": "ㅂ", "ㅆ": "ㅅ", "ㅉ": "ㅈ"}


def 첫소리(s: str) -> str:
    if not "가" <= s[0] <= "힣":
        return "#"
    c = 초성[(ord(s[0]) - 0xAC00) // 588]
    return 기본.get(c, c)


줄 = []
지금 = None
for 용어, 영문, 뜻, _ in sorted(KO, key=lambda r: r[0]):
    c = 첫소리(용어)
    if c != 지금:
        지금 = c
        줄 += ["", f"### {c}" if c != "#" else "### 숫자로 시작", "", "| 용어 | 영문 | 뜻 | 장 |", "|---|---|---|---|"]
    줄.append(f"| {용어} | {영문} | {뜻} | {장[용어]}장 |")
줄 += ["", "## D.2 영문으로 쓰는 용어", "", "약자나 이름을 영문 그대로 부르는 용어는 알파벳순으로 따로 모았습니다.", "",
       "| 용어 | 풀어 쓴 이름 | 뜻 | 장 |", "|---|---|---|---|"]
for 용어, 영문, 뜻, _ in sorted(EN, key=lambda r: r[0].lower()):
    줄.append(f"| {용어} | {영문 or '—'} | {뜻} | {장[용어]}장 |")
머리 = (여기 / "head.md").read_text(encoding="utf-8")
꼬리 = (여기 / "tail.md").read_text(encoding="utf-8")
Path(sys.argv[1]).write_text(머리.rstrip() + "\n" + "\n".join(줄) + "\n\n" + 꼬리, encoding="utf-8")
print("한글", len(KO), "영문", len(EN), "합계", len(KO) + len(EN))
print(sorted(Counter(장.values()).items()))
