"""3권 예제 환경 점검: 파이썬, 운영체제, 패키지 버전, 신경망 장치."""
import platform
import sys
from importlib.metadata import version

import torch

print(f"파이썬 {sys.version.split()[0]} / {platform.system()} {platform.machine()}")
for 패키지 in ["mujoco", "numpy", "scipy", "matplotlib", "opencv-python-headless", "pyserial",
              "torch", "torchvision", "gymnasium", "transformers", "anthropic"]:
    print(f"  {패키지:24s} {version(패키지)}")
print("CUDA 사용 가능:", torch.cuda.is_available(), "/ MPS 사용 가능:", torch.backends.mps.is_available())
