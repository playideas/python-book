"""11장 그림 도구: 방 평면도를 matplotlib 칸에 그린다."""
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import mujoco

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


def 방_그리기(칸, 모델: mujoco.MjModel, 색: str = "0.75") -> None:
    """방의 벽·섬·기둥·상자를 위에서 본 모양으로 그린다(로봇 몸체는 빼고)."""
    로봇 = 모델.body("robot").id
    for g in range(모델.ngeom):
        종류, 크기, (x, y, _) = 모델.geom_type[g], 모델.geom_size[g], 모델.geom_pos[g]
        if 모델.geom_bodyid[g] == 로봇:
            continue
        if 종류 == mujoco.mjtGeom.mjGEOM_BOX:
            칸.add_patch(patches.Rectangle((x - 크기[0], y - 크기[1]), 2 * 크기[0], 2 * 크기[1], color=색, lw=0))
        elif 종류 == mujoco.mjtGeom.mjGEOM_CYLINDER:
            칸.add_patch(patches.Circle((x, y), 크기[0], color=색, lw=0))
    칸.set_xlim(-0.5, 10.5)
    칸.set_ylim(-0.5, 8.5)
    칸.set_aspect("equal")
