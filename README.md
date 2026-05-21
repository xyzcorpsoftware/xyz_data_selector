# xyz_data_selector 사용 가이드

`xyz_data_selector`는 이미지 데이터셋과 Labelme 형식의 bbox 라벨을 확인하고, 필요한 샘플만 골라서 추출하거나 작업 단위로 나누기 위한 로컬 Python 도구입니다.

주요 기능은 다음과 같습니다.

- 이미지와 Labelme bbox 라벨을 OpenCV 창에서 함께 확인
- 키보드로 샘플 체크 및 타입 분류
- 체크한 샘플 목록을 파일로 저장
- 저장된 목록 기준으로 이미지/라벨 복사 또는 이동
- 이미지/라벨 쌍을 일정 개수 단위의 task 폴더로 분할

## 설치

Python 3.9 기반 conda 환경을 권장합니다. OpenCV GUI 창(`cv2.imshow`, `cv2.waitKey`, trackbar)을 사용하므로, OpenCV는 `conda-forge` 채널의 `opencv` 패키지를 사용합니다.

환경 파일로 설치:

```bash
conda env create -f environment.yml
conda activate xyz_data_selector
```

직접 설치:

```bash
conda create -n xyz_data_selector python=3.9
conda activate xyz_data_selector
conda install -c conda-forge opencv numpy tqdm
```

이미 환경을 만들어 둔 경우에는 활성화한 뒤 OpenCV를 설치합니다.

```bash
conda activate xyz_data_selector
conda install -c conda-forge opencv
```

설치 후 conda 환경이 활성화된 상태에서는 `python` 명령으로 스크립트를 실행합니다.

## 데이터셋 구조

이 도구는 수집 세션 하나를 하나의 데이터셋 폴더로 다룹니다. 데이터셋 폴더 이름은 자유롭게 정해도 되지만, 그 안에는 기본적으로 `images/`와 `bbox/`가 있어야 합니다.

```text
DATASET_FOLDER/
  images/
    sample_001.png
    sample_002.png
  bbox/
    sample_001.json
    sample_002.json
```

- `images/`: 원본 이미지 폴더
- `bbox/`: Labelme JSON 라벨 폴더
- 이미지 파일명과 라벨 파일명은 확장자를 제외하고 같아야 합니다.
- 현재 기본 라벨 타입은 `Labelme_BBox`이며, Labelme의 `rectangle` shape를 bbox로 읽습니다.

여러 수집 세션을 한 상위 폴더에 모아두는 경우에는 개별 세션 폴더를 지정하거나, `--sessions` 옵션으로 상위 폴더 아래의 모든 세션을 순서대로 확인할 수 있습니다.

```text
datasets/
  SESSION_A/
    images/
    bbox/
  SESSION_B/
    images/
    bbox/
```

예를 들어 `SESSION_A`를 확인하려면:

```bash
python 1_select_sample.py --base-path /path/to/datasets/SESSION_A
```

상위 폴더 안의 모든 세션을 이어서 확인하려면:

```bash
python 1_select_sample.py --base-path /path/to/datasets --sessions
```

## 1. 샘플 확인 및 선택

[1_select_sample.py](1_select_sample.py)는 이미지와 bbox 라벨을 함께 보여주는 확인용 플레이어입니다.

기본 실행:

```bash
python 1_select_sample.py --base-path /path/to/DATASET_FOLDER
```

여러 세션이 들어 있는 상위 폴더를 한 번에 확인하려면:

```bash
python 1_select_sample.py --base-path /path/to/datasets --sessions
```

이 경우 `images/`와 `bbox/`를 둘 다 가진 하위 폴더만 세션으로 인식합니다.

기본 클래스 설정은 `cup` 라벨을 바로 볼 수 있도록 준비되어 있습니다. 지금 수집하는 컵 데이터셋처럼 라벨이 `cup`이면 `--class-config` 없이 실행해도 됩니다.

`--target`을 생략하면 데이터셋 폴더명이 체크포인트와 체크 목록 파일 이름에 사용됩니다.

```bash
python 1_select_sample.py \
  --base-path /path/to/DATASET_FOLDER \
  --target my_review_session
```

이미지/라벨 폴더명이 기본값인 `images`, `bbox`와 다르면 아래처럼 지정합니다.

```bash
python 1_select_sample.py \
  --base-path /path/to/DATASET_FOLDER \
  --image-sub-path images \
  --label-sub-path bbox
```

이미지 확장자를 지정하려면 `--valid-exts`를 사용합니다.

```bash
python 1_select_sample.py \
  --base-path /path/to/DATASET_FOLDER \
  --valid-exts jpg,png,jpeg,bmp
```

기본값과 다른 클래스 이름 또는 색상을 쓰는 데이터셋은 JSON 파일로 설정을 분리합니다.

```bash
python 1_select_sample.py \
  --base-path /path/to/DATASET_FOLDER \
  --class-config examples/class_config.json
```

`examples/class_config.json` 형식:

```json
{
  "classes": {
    "BG": 0,
    "cup": 1,
    "pedestrian": 2
  },
  "colors": [
    [0, 0, 0],
    [255, 0, 255],
    [255, 255, 0]
  ]
}
```

`1`-`9` 체크 타입의 표시 이름은 별도 JSON으로 지정할 수 있습니다.
별도 지정하지 않으면 기본 타입 이름이 사용됩니다.

| 키 | 기본 타입 이름 |
| --- | --- |
| `1` | `bbox_fix` |
| `2` | `missing_object` |
| `3` | `wrong_class` |
| `4` | `needs_review` |
| `5` | `image_quality` |
| `6` | `relabel` |
| `7` | `review_7` |
| `8` | `review_8` |
| `9` | `relabel` |

```bash
python 1_select_sample.py \
  --base-path /path/to/DATASET_FOLDER \
  --type-labels examples/type_labels.json
```

사용 가능한 옵션은 다음 명령으로 확인할 수 있습니다.

```bash
python 1_select_sample.py --help
```

키 입력이 의도대로 동작하지 않는지 확인하려면 `--debug-keys`를 붙여 실행합니다.

```bash
python 1_select_sample.py \
  --base-path /path/to/DATASET_FOLDER \
  --debug-keys
```

### 주요 단축키

| 키 | 동작 |
| --- | --- |
| `a`, `←` | 이전 이미지 |
| `d`, `→` | 다음 이미지 |
| `f` | 여러 장 뒤로 이동 |
| `h` | 여러 장 앞으로 이동 |
| `z` | 확대 |
| `c` | 축소 |
| `1`-`9` | 현재 이미지에 타입 지정 |
| `s` | 기본 체크 토글 |
| `w` | 현재 이미지 체크 삭제 |
| `p` | 체크 목록 수동 저장 |
| `t` | 현재 화면 캡처 저장 |
| `m` | 라벨 텍스트 표시 토글 |
| `/` | 트랙바 업데이트 토글 |
| `<`, `>` | bbox 선 두께 조절 |
| `{`, `}` | 라벨 글자 크기 조절 |
| `Space` | 자동 재생 토글 |
| `q` | 종료 |

키 입력은 터미널이 아니라 OpenCV 이미지 창에 포커스가 있을 때 동작합니다.
단축키는 macOS, Ubuntu, Windows 모두 **영문 입력 상태**에서 사용하는 것을 권장합니다. 한글/일본어/중국어 같은 IME 입력 상태에서는 OpenCV backend와 OS에 따라 letter key의 raw code가 다르게 들어올 수 있습니다.
macOS 한글 입력기에서 관측된 주요 이동/종료 키는 일부 보정되어 있지만, 가장 안정적인 방법은 영문 입력 상태로 전환하거나 `←`, `→` 방향키를 사용하는 것입니다.

선택 상태는 화면 상단에 표시됩니다. 현재 이미지가 선택됐는지, 전체 선택 개수, 타입별 개수를 바로 확인할 수 있습니다.

체크포인트와 체크 목록은 데이터셋 루트에 저장됩니다. `1`-`9`, `s`, `w`로 선택 상태가 바뀔 때 체크 목록은 자동 저장되므로, 보통 `p`를 따로 누르지 않아도 됩니다.

```text
DATASET_FOLDER/
  {target}_check_point.json
  {target}_base_check_file_list.txt
  {target}_check_file_list.txt
```

`target`은 `--target`으로 지정하거나, 생략 시 데이터셋 폴더명으로 자동 지정됩니다.

항상 첫 프레임부터 다시 시작하려면 `--reset-checkpoint`를 사용합니다. 이 옵션은 기존 체크 목록은 유지하고, 마지막으로 보던 위치만 초기화합니다.

```bash
python 1_select_sample.py \
  --base-path /path/to/DATASET_FOLDER \
  --reset-checkpoint
```

체크 목록까지 완전히 초기화하려면 `{target}_base_check_file_list.txt`, `{target}_check_file_list.txt` 파일을 삭제합니다.

## 2. 체크한 데이터 추출

[2_data_extract_test.py](2_data_extract_test.py)는 저장된 체크 목록을 기준으로 이미지와 라벨을 별도 폴더로 복사하거나 이동합니다.

기본 실행:

```bash
python 2_data_extract_test.py --base-path /path/to/DATASET_FOLDER
```

체크 목록 파일을 직접 지정하려면 `--file-list-pathname`을 사용합니다.

```bash
python 2_data_extract_test.py \
  --base-path /path/to/DATASET_FOLDER \
  --file-list-pathname /path/to/check_file_list.txt
```

주요 옵션:

| 옵션 | 설명 |
| --- | --- |
| `--target` | 체크 목록 파일 이름에 사용할 세션 이름. 생략 시 데이터셋 폴더명 |
| `--save-path` | 추출 결과 저장 경로. 생략 시 `DATASET_FOLDER/selected_dataset` |
| `--class-config` | 클래스 이름과 bbox 색상 JSON 파일 |
| `--check-mode` | `list` 또는 `pos` |
| `--move` | 복사 대신 이동 |
| `--type-folders` | 타입별 하위 폴더를 만드는 기존 방식으로 저장 |
| `--data-merging` | 호환성용 옵션. 현재 기본 출력은 이미 통합 폴더 구조 |
| `--separate-folders` | 호환성용 옵션. 현재 기본 출력은 이미 `images/`, `bbox/` 분리 구조 |

기본 출력 경로는 아래와 같습니다.

```text
DATASET_FOLDER/
  selected_dataset/
    images/
      selected image files
    bbox/
      selected label files
    selected_samples.csv
```

`selected_samples.csv`에는 추출된 파일명, 체크 타입, 이미지 경로, 라벨 경로가 기록됩니다.

타입별 폴더를 따로 만들고 싶으면 `--type-folders`를 사용합니다.

## 3. 작업 단위로 데이터 분할

[3_data_allocation.py](3_data_allocation.py)는 이미지와 라벨 쌍을 일정 개수 단위로 나누어 task 폴더를 만듭니다.

기본 실행:

```bash
python 3_data_allocation.py --base-path /path/to/DATASET_FOLDER
```

예를 들어 이미지/라벨 쌍을 100개씩 나누려면:

```bash
python 3_data_allocation.py \
  --base-path /path/to/DATASET_FOLDER \
  --num-data 100
```

주요 옵션:

| 옵션 | 설명 |
| --- | --- |
| `--out-path` | task 출력 루트. 생략 시 `DATASET_FOLDER/task` |
| `--item` | task item 이름. 기본값은 `1` |
| `--num-data` | task 폴더 하나에 넣을 이미지/라벨 쌍 개수 |
| `--valid-exts` | 쉼표로 구분한 이미지 확장자. 기본값은 `jpg,png` |
| `--label-ext` | 라벨 확장자. 기본값은 `.json` |
| `--shuffle` | 분할 전에 파일 순서를 섞음 |

예를 들어 `--num-data 5`이면 이미지/라벨 쌍을 5개씩 나누어 아래처럼 저장합니다.

```text
task/
  1/
    0/
      image files
      label files
    1/
      image files
      label files
```

## 설정 파일 구조

샘플 확인과 데이터 추출 스크립트는 공통적으로 `base_data`와 `sub_data` 설정을 사용합니다.

```python
file_config = {
    "base_data": {
        "sub_path": "images",
        "type": "image",
        "prefix_name": None,
        "label_color": None,
        "class_infor": None,
        "roi_list": None,
        "valid_exts": ["jpg", "gif", "png", "tga", "jpeg", "JPG", "bmp"],
    },
    "sub_data": {
        "Labelme_BBox": {
            "sub_path": "bbox",
            "type": "Labelme_BBox",
            "path": None,
            "prefix_name": "",
            "label_color": label_colors,
            "class_infor": class_info,
            "check_draw_objs": False,
            "draw_place_name": "base_data",
            "draw_roi_name": None,
        }
    }
}
```

주요 항목은 다음과 같습니다.

| 항목 | 설명 |
| --- | --- |
| `sub_path` | `base_path` 아래의 하위 폴더명 |
| `type` | 데이터 타입. 이미지면 `image`, Labelme bbox면 `Labelme_BBox` |
| `prefix_name` | 이미지명과 라벨명이 prefix만 다른 경우 변환에 사용 |
| `label_color` | 클래스별 bbox 색상 |
| `class_infor` | 클래스 이름과 ID 매핑 |
| `draw_place_name` | 라벨을 어느 이미지 위에 그릴지 지정 |

## 현재 구현 기준의 주의사항

- `--base-path`에는 `images/`, `bbox/`를 포함하는 개별 데이터셋 폴더를 지정합니다.
- 기본 클래스 설정은 `cup` 라벨을 포함합니다. 다른 클래스 체계를 쓰면 `--class-config` JSON 파일로 지정합니다.
- Labelme 라벨은 `rectangle` shape 중심으로 처리됩니다.
- 이미지 파일 확장자는 기본적으로 `jpg`, `gif`, `png`, `tga`, `jpeg`, `JPG`, `bmp`를 찾습니다.
- OpenCV 창을 띄우기 때문에 서버나 headless 환경에서는 별도 설정 없이 실행하기 어렵습니다.
- public 저장소에 올리지 않아야 하는 로컬 설정, IDE 설정, 캐시 파일은 `.gitignore`에 포함되어 있습니다.

## 변경 사항 메모

최근 버전에서는 다음 정리를 반영했습니다.

- `environment.yml` 추가 및 conda-forge OpenCV 설치 기준 정리
- 세 실행 스크립트의 Windows 하드코딩 경로 제거 및 CLI 인자화
- 클래스/색상 설정과 체크 타입 라벨의 JSON 파일 분리
- bbox 영역 교차 계산, 파일명 생성, shuffle, 추출 폴더 설정 관련 런타임 버그 수정
