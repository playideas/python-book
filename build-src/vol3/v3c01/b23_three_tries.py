from 피하기도구 import 결과, 달리기

시도들 = [("1. 목표만 보고 간다", False, False),
        ("2. 장애물에서 밀려난다", True, False),
        ("3. 밀려나면서 옆으로 돈다", True, True)]
for 이름, 밀어내기, 옆으로 in 시도들:
    print(이름)
    print("  ", 결과(달리기(밀어내기, 옆으로)))
