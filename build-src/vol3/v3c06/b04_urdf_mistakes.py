import subprocess
import tempfile
from pathlib import Path

from urdf_parser_py.urdf import URDF

링크둘 = '<link name="a"/><link name="b"/>'
실수들 = {
    "회전 관절에 limit 없음": f'<joint name="j" type="revolute"><parent link="a"/><child link="b"/>'
                         f'<axis xyz="0 0 1"/></joint>',
    "없는 링크 이름(오타)": '<joint name="j" type="fixed"><parent link="a"/><child link="bb"/></joint>',
    "어디에도 안 이어진 링크": '<link name="c"/><joint name="j" type="fixed"><parent link="a"/><child link="b"/></joint>',
}
with tempfile.TemporaryDirectory() as 폴더:
    for 설명, 본문 in 실수들.items():
        파일 = Path(폴더) / "test.urdf"
        파일.write_text(f'<robot name="r">{링크둘}{본문}</robot>')
        결과 = subprocess.run(["check_urdf", str(파일)], capture_output=True, text=True)
        첫_오류 = next(줄 for 줄 in (결과.stdout + 결과.stderr).splitlines() if 줄.startswith("Error"))
        try:
            뿌리 = URDF.from_xml_file(str(파일)).get_root()   # 읽기만 하면 통과, 뿌리를 찾을 때 걸린다
            파이썬 = f"통과(뿌리 {뿌리})"
        except AssertionError as 오류:
            파이썬 = f"거부({오류})"
        print(f"[{설명}]\n  check_urdf     : {첫_오류.removeprefix('Error:').strip()}\n  urdf_parser_py : {파이썬}")
