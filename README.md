# xyz_data_selector 사용 가이드

`xyz_data_selector`는 이미지 데이터셋과 Labelme 형식의 bbox 라벨을 확인하고, 필요한 샘플만 골라서 추출하거나 작업 단위로 나누기 위한 로컬 Python 도구입니다.

주요 기능은 다음과 같습니다.

- 이미지와 Labelme bbox 라벨을 OpenCV 창에서 함께 확인
- 키보드로 샘플 체크 및 타입 분류
- 체크한 샘플 목록을 파일로 저장
- 저장된 목록 기준으로 이미지/라벨 복사 또는 이동
- 이미지/라벨 쌍을 일정 개수 단위의 task 폴더로 분할

## 설치

Python 3.9 이상 환경을 권장합니다.

macOS / Ubuntu:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Windows cmd:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

설치 후 가상환경이 활성화된 상태에서는 `python` 명령으로 스크립트를 실행합니다.

## 데이터셋 구조

기본 예제는 아래와 같은 폴더 구조를 기대합니다.

```text
DATASET_ROOT/
  images/
    sample_001.jpg
    sample_002.jpg
  bbox/
    sample_001.json
    sample_002.json
```

- `images/`: 원본 이미지 폴더
- `bbox/`: Labelme JSON 라벨 폴더
- 이미지 파일명과 라벨 파일명은 확장자를 제외하고 같아야 합니다.
- 현재 기본 라벨 타입은 `Labelme_BBox`이며, Labelme의 `rectangle` shape를 bbox로 읽습니다.

## 1. 샘플 확인 및 선택

[1_select_sample.py](1_select_sample.py)는 이미지와 bbox 라벨을 함께 보여주는 확인용 플레이어입니다.

기본 실행:

```bash
python 1_select_sample.py --base-path /path/to/DATASET_ROOT
```

`--target`을 생략하면 데이터셋 루트 폴더명이 체크포인트와 체크 목록 파일 이름에 사용됩니다.

```bash
python 1_select_sample.py \
  --base-path /path/to/DATASET_ROOT \
  --target 20260514T080008Z-3-001
```

이미지/라벨 폴더명이 기본값인 `images`, `bbox`와 다르면 아래처럼 지정합니다.

```bash
python 1_select_sample.py \
  --base-path /path/to/DATASET_ROOT \
  --image-sub-path images \
  --label-sub-path bbox
```

이미지 확장자를 지정하려면 `--valid-exts`를 사용합니다.

```bash
python 1_select_sample.py \
  --base-path /path/to/DATASET_ROOT \
  --valid-exts jpg,png,jpeg,bmp
```

클래스 이름과 bbox 색상은 JSON 파일로 분리할 수 있습니다.

```bash
python 1_select_sample.py \
  --base-path /path/to/DATASET_ROOT \
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

```bash
python 1_select_sample.py \
  --base-path /path/to/DATASET_ROOT \
  --type-labels examples/type_labels.json
```

사용 가능한 옵션은 다음 명령으로 확인할 수 있습니다.

```bash
python 1_select_sample.py --help
```

### 주요 단축키

| 키 | 동작 |
| --- | --- |
| `a` | 이전 이미지 |
| `d` | 다음 이미지 |
| `f` | 여러 장 뒤로 이동 |
| `h` | 여러 장 앞으로 이동 |
| `z` | 확대 |
| `c` | 축소 |
| `1`-`9` | 현재 이미지에 타입 지정 |
| `s` | 기본 체크 토글 |
| `w` | 현재 이미지 체크 삭제 |
| `p` | 체크 목록 저장 |
| `t` | 현재 화면 캡처 저장 |
| `m` | 라벨 텍스트 표시 토글 |
| `/` | 트랙바 업데이트 토글 |
| `<`, `>` | bbox 선 두께 조절 |
| `{`, `}` | 라벨 글자 크기 조절 |
| `Space` | 자동 재생 토글 |
| `Esc` | 종료 |

체크포인트와 체크 목록은 데이터셋 루트에 저장됩니다.

```text
DATASET_ROOT/
  {target}_check_point.json
  {target}_base_check_file_list.txt
  {target}_check_file_list.txt
```

`target`은 `--target`으로 지정하거나, 생략 시 데이터셋 루트 폴더명으로 자동 지정됩니다.

## 2. 체크한 데이터 추출

[2_data_extract_test.py](2_data_extract_test.py)는 저장된 체크 목록을 기준으로 이미지와 라벨을 별도 폴더로 복사하거나 이동합니다.

기본 실행:

```bash
python 2_data_extract_test.py --base-path /path/to/DATASET_ROOT
```

체크 목록 파일을 직접 지정하려면 `--file-list-pathname`을 사용합니다.

```bash
python 2_data_extract_test.py \
  --base-path /path/to/DATASET_ROOT \
  --file-list-pathname /path/to/check_file_list.txt
```

주요 옵션:

| 옵션 | 설명 |
| --- | --- |
| `--target` | 체크 목록 파일 이름에 사용할 세션 이름. 생략 시 데이터셋 루트 폴더명 |
| `--save-path` | 추출 결과 저장 경로. 생략 시 `DATASET_ROOT/{target}` |
| `--class-config` | 클래스 이름과 bbox 색상 JSON 파일 |
| `--check-mode` | `list` 또는 `pos` |
| `--move` | 복사 대신 이동 |
| `--data-merging` | 타입별 결과를 한 폴더로 합침 |
| `--separate-folders` | 이미지와 라벨을 각각 하위 폴더에 저장 |

기본 출력 경로는 아래와 같습니다.

```text
DATASET_ROOT/
  {target}/
    0_{target}_{type}/
      images 또는 이미지 파일
      bbox 또는 라벨 파일
```

## 3. 작업 단위로 데이터 분할

[3_data_allocation.py](3_data_allocation.py)는 이미지와 라벨 쌍을 일정 개수 단위로 나누어 task 폴더를 만듭니다.

기본 실행:

```bash
python 3_data_allocation.py --base-path /path/to/DATASET_ROOT
```

예를 들어 이미지/라벨 쌍을 100개씩 나누려면:

```bash
python 3_data_allocation.py \
  --base-path /path/to/DATASET_ROOT \
  --num-data 100
```

주요 옵션:

| 옵션 | 설명 |
| --- | --- |
| `--out-path` | task 출력 루트. 생략 시 `DATASET_ROOT/task` |
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

- 데이터셋 경로는 `--base-path`로 지정합니다.
- 클래스 이름과 bbox 색상은 `--class-config` JSON 파일로 지정합니다.
- Labelme 라벨은 `rectangle` shape 중심으로 처리됩니다.
- 이미지 파일 확장자는 기본적으로 `jpg`, `gif`, `png`, `tga`, `jpeg`, `JPG`, `bmp`를 찾습니다.
- OpenCV 창을 띄우기 때문에 서버나 headless 환경에서는 별도 설정 없이 실행하기 어렵습니다.
- public 저장소에 올리지 않아야 하는 로컬 설정, IDE 설정, 캐시 파일은 `.gitignore`에 포함되어 있습니다.

## 변경 사항 메모

최근 버전에서는 다음 정리를 반영했습니다.

- `requirements.txt` 추가
- 세 실행 스크립트의 Windows 하드코딩 경로 제거 및 CLI 인자화
- 클래스/색상 설정과 체크 타입 라벨의 JSON 파일 분리
- bbox 영역 교차 계산, 파일명 생성, shuffle, 추출 폴더 설정 관련 런타임 버그 수정
