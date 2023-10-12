##Video captioning setup
BMT 도구를 사용하여 video captioning 모델을 설정하고 학습하는 기능입니다.
1. BMT Repository Clone
2. feature 및 단어 임베딩 다운로드
3. conda 환경 설정
4. captioning module 훈련
5. proposal generation 모듈 훈련
6. I3D Feature Extraction & VGGish Feature Extraction
7. 추출된 특징을 바탕으로 BMT 도구를 사용하여 video segment에 대한 captiong 생성

**기능 구현 상세**

```bash
git clone --recursive https://github.com/v-iashin/BMT.git
bash ./download_data.sh
conda env create -f ./conda_env.yml
conda activate bmt
python -m spacy download en
python main.py \
    --procedure train_cap \
    --B 32
python main.py \
    --procedure train_prop \
    --pretrained_cap_model_path /your_exp_path/best_cap_model.pt \
    --B 16
```

- BMT repository에서 필요한 모델 코드 및 데이터를 가져옵니다.
- 필요한 특징 (I3D 및 VGGish) 및 단어 임베딩 (GloVe) 다운로드합니다.
- 메뉴얼에 맞게 Conda 환경을 설정하여 의존성 문제 해결합니다.
- Ground truth proposals에 대한 captioning 모듈 및 pre-trained encoder를 사용한 proposal generator 모듈을 학습합니다.
- I3D 특징을 추출하기 위해 **`submodules/video_features`** 디렉토리로 이동합니다.
- VGGish 특징은 **`vggish`** conda 환경에서 추출합니다.
- 메인 BMT 디렉토리로 복귀한 후, 필요한 인수와 함께 **`single_video_prediction.py`** 스크립트를 실행하여 **`bmt`** conda 환경을 활성화합니다.

##Real-time captioning과 데이터 전송
특징 추출과 캡셔닝이 실시간으로 이루어지도록 하기 위해 앞의 구현을 통합적으로 send1.py 스크립트를 구현하고 생성된 캡션은 웹소켓을 사용하여 JSON 형식으로 서버에 전송됩니다.

- `def run_command(command):` 주어진 **`command`**를 외부 명령어로 실생한 후 실행한 명령어의 표준 출력과 표준 오류를 반환합니다.
- 주어진 비디오에서 I3D와 VGGish 특징을 추출한 후, 이 특징들을 기반으로 비디오에 대한 캡션을 생성합니다.
- **`extract_captions_from_output`** 함수를 사용하여 캡션 결과를 추출합니다.
- 캡션 데이터를 JSON 형식으로 웹소켓 서버에 전송합니다. 서버 주소는 **`"ws://117.16.137.205:8080/ai"`**로 설정되어 있습니다.
- 전체 프로세스는 스트림 라인화되어 하나의 명령어로 실행됩니다.
```
python send1.py —video_paths test/testvideo.mp4
```
