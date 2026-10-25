from 언어계획 import 언어계획기
from 지시수행 import 이름표

이름들 = list(이름표)
지시들 = ["빨간 상자를 파란 그릇에 넣어 줘", "공을 그릇에 담아", "노란 컵이랑 초록 상자를 그릇에 넣어",
         "초록 상자는 그릇에 넣지 마", "빨간 상자를 창밖으로 던져 줘", "Put the green box in the bowl", "고마워"]
for 이름 in ["Qwen/Qwen2.5-0.5B-Instruct", "Qwen/Qwen2.5-1.5B-Instruct"]:
    계획기 = 언어계획기(이름)
    print(f"== {이름}")
    for 지시 in 지시들:
        계획, 글 = 계획기.계획(지시, 이름들)
        요약 = " → ".join(f"{단계.get('기술')}({단계.get('대상')})" for 단계 in 계획 if isinstance(단계, dict)) \
            if isinstance(계획, list) else f"목록이 아님: {글[:30]}"
        print(f"{지시} | {요약}")
