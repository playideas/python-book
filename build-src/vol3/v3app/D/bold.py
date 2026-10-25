"""3권 본문(코드 밖)에서 굵게 쓴 말과 처음 나온 장, 앞뒤 글을 모은다."""
import re, json
from pathlib import Path
CH = Path(__file__).resolve().parents[4] / "manuscript-vol3" / "chapters"
처음 = {}
for f in sorted(CH.glob("*.md")):
    n = int(f.name[:2]); 코드 = False
    for 줄 in f.read_text(encoding="utf-8").splitlines():
        if 줄.startswith("```"): 코드 = not 코드; continue
        if 코드 or 줄.startswith(">") and "학습 목표" in 줄: continue
        if 줄.startswith("- **") and 줄.count("**") >= 2 and ":" in 줄[:40] and "정리" in "": pass
        for m in re.finditer(r"\*\*([^*\n]{1,40}?)\*\*\s*(\([^)\n]{1,60}\))?", 줄):
            말 = m.group(1).strip(); 괄호 = (m.group(2) or "")
            if 말 not in 처음:
                i = m.start(); 처음[말] = (n, 괄호, 줄[max(0, i-60): m.end()+120])
json.dump(처음, open("bold.json", "w"), ensure_ascii=False, indent=0)
for 말, (n, 괄호, ctx) in 처음.items():
    print(f"{n:2d} | {말} {괄호}")
print(len(처음))
