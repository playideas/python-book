# 딥러닝 노트북

파이썬을 아는 입문자가 혼자 따라 하며 딥러닝을 익히도록 만든 노트북 11개입니다. 텐서에서 시작해 CNN, 생성 모델, Transformer를 거쳐 LLM까지 다룹니다.

**저자**: 이창민

이 저장소의 책과 함께 볼 수 있습니다. 책은 체계적인 설명을, 노트북은 직접 돌려 보는 실습을 맡습니다. 노트북만으로도 공부할 수 있습니다.

## 강의 구성

| 강 | 파일 | 주제 |
|---|---|---|
| 1 | `01_pytorch_basics.ipynb` | 텐서, 자동 미분, 첫 학습 코드 |
| 2 | `02_neural_networks.ipynb` | 신경망, 손실 함수, 옵티마이저, 스케줄러, 초기화 |
| 3 | `03_cnn.ipynb` | 합성곱, 풀링, CNN, Siamese, 웹 배포 |
| 4 | `04_generalization.ipynb` | 과적합, 증강, BatchNorm, Dropout, 규제, 앙상블, 실험 기록 |
| 5 | `05_transfer_learning.ipynb` | 대표 모델, 저장과 불러오기, 동결, 파인튜닝, timm |
| 6 | `06_object_detection.ipynb` | 라벨링, COCO, R-CNN 계열, RT-DETR, YOLO, 직접 학습 |
| 7 | `07_representation_segmentation.ipynb` | t-SNE, UMAP, 오토인코더, VAE, FCN, U-Net, Mask R-CNN, SAM 2 |
| 8 | `08_generative_models.ipynb` | 스타일 전이, GAN, DCGAN, pix2pix, DDPM, 잠재 확산 |
| 9 | `09_sequence_attention.ipynb` | RNN, LSTM, GRU, 어텐션, Transformer, ViT, BERT, CLIP |
| 10 | `10_analysis_deployment.ipynb` | CAM, Grad-CAM, ONNX, 하이퍼파라미터 탐색, 병렬 학습, 배포 |
| 11 | `11_llm.ipynb` | 토큰, 처음부터 만드는 GPT, 파인튜닝, 평가, RAG, 도구 호출, 로컬 실행 |

앞 강의의 내용을 뒤에서 씁니다. 처음이라면 1강부터 차례로 보세요. 각 노트북 앞머리에 예상 시간과 필수/선택 절, 막혔을 때 볼 곳이 있습니다.

## 실행

- Google Colab을 기준으로 썼습니다. 파일을 Colab에서 열고 "모두 실행"을 누르면 됩니다. 필요한 데이터와 패키지는 노트북 안에서 받습니다.
- 저장된 출력은 저자의 Mac(MPS, CPU)에서 실행한 결과입니다. 난수와 환경에 따라 수치가 조금씩 다를 수 있습니다.
- 노트북 11개 모두 Linux의 NVIDIA GPU(RTX 4090 두 장, RTX 6000 Ada)에서 처음부터 끝까지, 학습 횟수를 줄이지 않고 실행해 에러 없이 끝나는 것을 확인했습니다. 패키지는 Colab처럼 각 노트북 첫 셀의 `%pip`로 설치했습니다. 10강의 여러 GPU 절도 GPU 두 장에서 확인했습니다.
- **Colab 자체에서는 아직 돌려 보지 않았습니다.** 예상 시간도 어림값입니다. 문제를 발견하면 알려 주세요.
- Colab 밖에서 실행한다면 Colab에 기본으로 있는 `opencv-python-headless`와 `jax`를 먼저 설치하세요(10강).
- 일부 학습은 저장 출력을 만들 때 횟수를 줄였습니다. 노트북 앞쪽의 값을 원래대로 바꾸면 전체 학습을 돌릴 수 있습니다.
- API 키가 필요한 선택 실습은 키가 없으면 건너뜁니다. 키는 코드에 넣지 말고 Colab의 보안 비밀(Secrets)에 두세요.

## 저장되지 않은 그림

실제 인물이 보이는 사진과 ImageNet, CIFAR-10 등 재배포 조건을 확인하지 못한 데이터의 사진은 저장 출력에서 뺐습니다. 코드는 그대로이니 실행하면 볼 수 있습니다.

## 라이선스

- **본문과 직접 그린 그림**: [CC BY 4.0](LICENSE-text)
- **코드**: [MIT](LICENSE)
- **제3자 자료**(가져온 코드, 데이터, 모델 가중치, 사진)는 위 라이선스에 포함되지 않습니다. 출처와 조건은 [NOTICE.md](NOTICE.md)에 있습니다. 일부 그림은 CC BY-SA를, 6강 YOLO 절은 AGPL-3.0을 따릅니다.
