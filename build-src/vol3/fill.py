"""3권: template.md의 <<CODE x>>/<<OUT x>>를 실제 코드와 실행 출력으로 채운다.

사용: uv run python build-src/vol3/fill.py <장 폴더> <원고 경로> <그림 폴더> [--ros]
각 블록은 examples/vol3의 고정 버전 환경에서, 그림 폴더를 작업 폴더로 삼아 실행한다
(블록이 저장하는 그림이 바로 원고의 그림 자리에 생긴다).
--ros: 5~6장처럼 ROS 2가 필요한 장. examples/vol3/ros/Dockerfile로 만든 이미지 안에서 실행한다
(장 폴더는 /src, 그림 폴더는 /out에 연결). 블록은 .py(파이썬) 또는 .sh(bash)다.
이름이 _host로 끝나는 블록(예: b20_path_plot_host.py)은 --ros 모드에서도 호스트 환경에서 실행한다
(컨테이너가 기록한 파일을 같은 그림 폴더에서 읽어 그림을 그릴 때).
<<FILE 파일이름 언어>>는 실행하지 않는 데이터 파일(URDF 등)을 장 폴더에서 읽어 그대로 싣는다.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "vol3"
ROS_IMAGE = "python-book-ros:lyrical"
ROS_TIMEOUT = 300
# 내려받는 사진·가중치는 저장소 밖 한곳에 둔다(그림 폴더 안에 data/가 생기지 않게)
DATA_DIR = Path(os.environ.get("BOOK_DATA_DIR", Path.home() / ".cache" / "python-book-data"))
BLOCK_ENV = {**os.environ, "BOOK_DATA_DIR": str(DATA_DIR),
             "TORCH_HOME": os.environ.get("TORCH_HOME", str(DATA_DIR / "torch"))}


def block_command(path: Path, cwd: Path, ros: bool) -> list[str]:
    if not ros or path.stem.endswith("_host"):
        return ["uv", "run", "-q", "--project", str(PROJECT), "python", "-W", "ignore", str(path)]
    runner = ["bash", f"/src/{path.name}"] if path.suffix == ".sh" else ["python3", "-W", "ignore", f"/src/{path.name}"]
    # --network none: 동시에 도는 다른 컨테이너의 ROS 노드·토픽이 DDS 탐색으로 섞이지 않게 격리한다
    return ["docker", "run", "--rm", "--network", "none", "-v", f"{path.parent}:/src:ro", "-v", f"{cwd}:/out", "-w", "/out",
            ROS_IMAGE] + runner


def run_block(path: Path, cwd: Path, ros: bool = False) -> str:
    r = subprocess.run(block_command(path, cwd, ros), capture_output=True, text=True, cwd=cwd, env=BLOCK_ENV,
                       timeout=ROS_TIMEOUT if ros else None)
    if r.returncode != 0:
        sys.exit(f"{path.stem} 실패:\n{r.stderr}")
    return r.stdout.rstrip("\n")


def main() -> None:
    chapter, dst, image_dir = (Path(a).resolve() for a in sys.argv[1:4])
    ros = "--ros" in sys.argv[4:]
    image_dir.mkdir(parents=True, exist_ok=True)
    t = (chapter / "template.md").read_text(encoding="utf-8")
    # <<FILE 파일이름 언어>>: 실행하지 않는 데이터 파일(URDF, xacro, launch 등)을 그대로 싣는다
    for name, lang in re.findall(r"<<FILE (\S+) (\w+)>>", t):
        body = (chapter / name).read_text(encoding="utf-8").rstrip("\n")
        t = t.replace(f"<<FILE {name} {lang}>>", f"```{lang}\n{body}\n```")
    names = list(dict.fromkeys(re.findall(r"<<(?:CODE|OUT) (\w+)>>", t)))
    for name in names:
        path = chapter / f"{name}.py"
        if not path.exists():
            path = chapter / f"{name}.sh"
        lang = "bash" if path.suffix == ".sh" else "python"
        src = path.read_text(encoding="utf-8").rstrip("\n")
        t = t.replace(f"<<CODE {name}>>", f"```{lang}\n{src}\n```")
        if f"<<OUT {name}>>" in t:
            t = t.replace(f"<<OUT {name}>>", f"```text\n{run_block(path, image_dir, ros)}\n```")
    assert not re.search(r"<<(?:CODE|OUT|FILE) \S+", t), "채우지 못한 자리가 남았다"
    dst.write_text(t, encoding="utf-8")
    print("blocks:", len(names))


if __name__ == "__main__":
    main()
