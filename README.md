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

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install numpy opencv-python tqdm
```

OpenCV GUI 창을 사용하므로, 화면이 있는 로컬 환경에서 실행해야 합니다.

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

실행 전 `base_path`를 자신의 데이터셋 루트 경로로 수정합니다.

```python
base_path = "C:/Project/dataset/20260514T080008Z-3-001"
```

클래스 정보와 색상도 데이터셋에 맞게 수정합니다.

```python
obj_cls = {"BG": 0, "cup": 1, "pedestrian": 2}
obj_color = [[0, 0, 0], [255, 0, 255], [255, 255, 0]]
```

실행:

```bash
python 1_select_sample.py
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

`target`은 예제 코드에서 아래 값으로 지정됩니다.

```python
target = "20260514T080008Z-3-001"
```

## 2. 체크한 데이터 추출

[2_data_extract_test.py](2_data_extract_test.py)는 저장된 체크 목록을 기준으로 이미지와 라벨을 별도 폴더로 복사하거나 이동합니다.

실행 전 `base_path`, 클래스 정보, 라벨 설정을 [1_select_sample.py](1_select_sample.py)와 동일하게 맞춥니다.

```python
base_path = "C:/Project/dataset/20260514T080008Z-3-001"
```

실행:

```bash
python 2_data_extract_test.py
```

기본 설정은 다음과 같습니다.

```python
'check_mode': "list"
'check_copy': True
'data_merging': False
'check_same_folder': True
```

- `check_mode`: 읽을 체크 목록 타입입니다. 예제는 `list` 모드입니다.
- `check_copy`: `True`이면 복사, `False`이면 이동합니다.
- `data_merging`: 타입별 결과를 한 폴더로 합칠지 여부입니다.
- `check_same_folder`: 이미지와 라벨을 같은 결과 폴더에 저장할지 여부입니다.

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

실행 전 아래 경로를 데이터셋에 맞게 수정합니다.

```python
sample = {
    "items": ["1"],
    "out_path": "C:/Project/dataset/20260514T080008Z-3-001/task",
    "check_copy": True,
    "1": {
        "num_data": 5,
        "data_path": "C:/Project/dataset/20260514T080008Z-3-001/images",
        "valid_exts": ["jpg", "png"],
        "label_path": "C:/Project/dataset/20260514T080008Z-3-001/bbox",
        "label_ext": ".json",
        "shuffle": False
    },
}
```

실행:

```bash
python 3_data_allocation.py
```

예를 들어 `num_data`가 `5`이면 이미지/라벨 쌍을 5개씩 나누어 아래처럼 저장합니다.

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

세 스크립트는 공통적으로 `base_data`와 `sub_data` 설정을 사용합니다.

```python
file_config = {
    "base_data": {
        "sub_path": "images",
        "type": "image",
        "prefix_name": None,
        "label_color": None,
        "class_infor": None,
        "roi_list": None,
    },
    "sub_data": {
        "Labelme_BBox": {
            "sub_path": "bbox",
            "type": "Labelme_BBox",
            "path": None,
            "prefix_name": "",
            "label_color": obj_color,
            "class_infor": obj_cls,
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

- 샘플 스크립트의 경로는 현재 하드코딩되어 있으므로 실행 전에 직접 수정해야 합니다.
- Labelme 라벨은 `rectangle` shape 중심으로 처리됩니다.
- 이미지 파일 확장자는 기본적으로 `jpg`, `gif`, `png`, `tga`, `jpeg`, `JPG`, `bmp`를 찾습니다.
- OpenCV 창을 띄우기 때문에 서버나 headless 환경에서는 별도 설정 없이 실행하기 어렵습니다.
- public 저장소에 올리지 않아야 하는 로컬 설정, IDE 설정, 캐시 파일은 `.gitignore`에 포함되어 있습니다.
