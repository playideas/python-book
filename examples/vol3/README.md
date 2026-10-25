# 3권 로봇 예제

3권의 코드 블록은 [`build-src/vol3/`](../../build-src/vol3/)에 블록 하나당 파일 하나로 들어 있습니다(`v3cNN/`이 N장, `v3app/`이 부록).
이 폴더는 그 블록을 실행할 고정 버전 환경(`pyproject.toml`, `uv.lock`)과 ROS 2 장(5·6장 등)용 Docker 이미지(`ros/Dockerfile`)입니다.

## 블록 하나 실행하기

[uv](https://docs.astral.sh/uv/)가 필요합니다. 블록은 그 장의 그림 폴더에서 실행해야 출력과 그림이 원고와 같은 자리에 생깁니다.

```bash
cd manuscript-vol3/assets/images/ch02
uv run --project ../../../../examples/vol3 python ../../../../build-src/vol3/v3c02/b01_two_frames.py
```

## 장 하나를 통째로 다시 만들기

`fill.py`는 장의 `template.md`에 있는 `<<CODE>>`/`<<OUT>>` 자리를 블록을 실제로 실행한 결과로 채워 원고를 씁니다.

```bash
uv run python build-src/vol3/fill.py build-src/vol3/v3c02 manuscript-vol3/chapters/02-frames-rotations.md manuscript-vol3/assets/images/ch02
```

ROS 2 장은 먼저 이미지를 만들고 `--ros`를 붙입니다(Docker 필요, ROS 2 Lyrical).

```bash
docker build -t python-book-ros:lyrical examples/vol3/ros
uv run python build-src/vol3/fill.py build-src/vol3/v3c05 manuscript-vol3/chapters/05-ros2-basics.md manuscript-vol3/assets/images/ch05 --ros
```

내려받는 사진과 사전학습 가중치는 `~/.cache/python-book-data`(환경 변수 `BOOK_DATA_DIR`로 변경)에 저장됩니다.
19장의 Claude 절은 `ANTHROPIC_API_KEY` 환경 변수가 있어야 실행되며(유료 API), 원고에는 2026년 10월에 한 번 실행한 출력을 실었습니다.

## 버전

파이썬 3.12, MuJoCo 3.17, NumPy 2.5, SciPy 1.18, matplotlib 3.11, OpenCV 5.0, PyTorch 2.14, Gymnasium 1.4. 정확한 버전은 `uv.lock`에 있습니다.
