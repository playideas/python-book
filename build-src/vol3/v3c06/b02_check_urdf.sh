# 이 스크립트가 있는 폴더의 URDF를 검사한다: 문법, 부모·자식 연결, 뿌리 링크
cd "$(dirname "$0")"
check_urdf 두관절팔.urdf
