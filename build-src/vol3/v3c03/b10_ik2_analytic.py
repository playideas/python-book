import numpy as np

위팔, 아래팔 = 0.4, 0.3


def 손끝(어깨: float, 팔꿈치: float) -> np.ndarray:
    return np.array([위팔 * np.cos(어깨) + 아래팔 * np.cos(어깨 + 팔꿈치),
                     위팔 * np.sin(어깨) + 아래팔 * np.sin(어깨 + 팔꿈치)])


def 역기구학2(x: float, y: float) -> list[tuple[float, float]]:
    """손끝 목표 (x, y) → 가능한 (어깨, 팔꿈치) 각도(rad) 목록. 0개, 1개, 2개일 수 있다."""
    c2 = (x**2 + y**2 - 위팔**2 - 아래팔**2) / (2 * 위팔 * 아래팔)    # 코사인 법칙
    if abs(c2) > 1:
        return []                                                 # 닿지 않는 곳
    각 = np.arccos(c2)
    팔꿈치들 = [각] if np.isclose(abs(c2), 1) else [-각, 각]       # 팔을 다 펴거나 접으면 답이 하나
    답 = []
    for 팔꿈치 in 팔꿈치들:
        어깨 = np.arctan2(y, x) - np.arctan2(아래팔 * np.sin(팔꿈치), 위팔 + 아래팔 * np.cos(팔꿈치))
        어깨 = (어깨 + np.pi) % (2 * np.pi) - np.pi                # -180~180도로 맞추기
        답.append((어깨, 팔꿈치))
    return 답


for 목표 in [(0.5, 0.3), (0.7, 0.0), (0.8, 0.2), (0.05, 0.0)]:
    답 = 역기구학2(*목표)
    print(f"목표 {목표}: 답 {len(답)}개")
    for 어깨, 팔꿈치 in 답:
        검산 = np.linalg.norm(손끝(어깨, 팔꿈치) - 목표)
        print(f"   어깨 {round(np.rad2deg(어깨), 1) + 0.0:6.1f}도, 팔꿈치 {round(np.rad2deg(팔꿈치), 1) + 0.0:6.1f}도 (검산 오차 {검산:.1e}m)")
