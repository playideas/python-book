import numpy as np

a = np.array([3.0, 4.0, 0.0])
b = np.array([1.0, 0.0, 0.0])

print("길이 |a|        :", np.linalg.norm(a))
print("단위 벡터 a/|a| :", a / np.linalg.norm(a))
print("내적 a·b        :", a @ b)                          # np.dot(a, b)와 같다
각도 = np.arccos(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
print(f"사이 각도       : {np.rad2deg(각도):.2f}도")
print("b 방향 성분     :", (a @ b) * b)                    # b가 단위 벡터라서 이렇게 쓴다
