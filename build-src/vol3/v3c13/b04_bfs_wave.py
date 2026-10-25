from collections import deque

# 작은 지도: '#'는 벽, S는 시작, G는 목표
지도 = ["..........",
        "....#.....",
        ".S..#..G..",
        "....#.....",
        "....####..",
        ".........."]
행수, 열수 = len(지도), len(지도[0])
시작 = next((r, c) for r in range(행수) for c in range(열수) if 지도[r][c] == "S")

걸음 = {시작: 0}
줄 = deque([시작])                         # 먼저 들어온 칸부터 꺼내는 줄(1권 8장의 deque)
while 줄:
    r, c = 줄.popleft()
    for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:      # 위아래 왼쪽 오른쪽 네 방향
        다음 = (r + dr, c + dc)
        if 0 <= 다음[0] < 행수 and 0 <= 다음[1] < 열수 and 지도[다음[0]][다음[1]] != "#" and 다음 not in 걸음:
            걸음[다음] = 걸음[(r, c)] + 1                  # 처음 닿은 순간의 걸음 수가 가장 적은 걸음 수
            줄.append(다음)

for r in range(행수):
    print(" ".join(" #" if 지도[r][c] == "#" else f"{걸음[(r, c)]:2d}" for c in range(열수)))
목표 = next((r, c) for r in range(행수) for c in range(열수) if 지도[r][c] == "G")
print("목표까지 가장 적은 걸음 수:", 걸음[목표])
