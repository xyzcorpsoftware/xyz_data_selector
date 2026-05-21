import json


DEFAULT_CLASS_INFO = {"BG": 0, "cup": 1, "pedestrian": 2}
DEFAULT_LABEL_COLORS = [[0, 0, 0], [255, 0, 255], [255, 255, 0]]
DEFAULT_VALID_EXTS = ["jpg", "gif", "png", "tga", "jpeg", "JPG", "bmp"]
DEFAULT_TYPE_LABELS = {
    "1": "bbox_fix",
    "2": "missing_object",
    "3": "wrong_class",
    "4": "needs_review",
    "5": "image_quality",
    "6": "relabel",
    "7": "review_7",
    "8": "review_8",
    "9": "relabel",
}


def parse_csv_list(value):
    return [item.strip() for item in value.split(",") if item.strip()]


def load_class_config(path):
    if path is None:
        return DEFAULT_CLASS_INFO, DEFAULT_LABEL_COLORS

    with open(path, "r") as f:
        data = json.load(f)

    class_info = data.get("classes", DEFAULT_CLASS_INFO)
    label_colors = data.get("colors", DEFAULT_LABEL_COLORS)
    return class_info, label_colors


def load_type_labels(path):
    if path is None:
        return DEFAULT_TYPE_LABELS

    with open(path, "r") as f:
        return json.load(f)


def build_file_config(image_sub_path, label_sub_path, class_info, label_colors, valid_exts=None):
    return {
        "base_data": {
            "sub_path": image_sub_path,
            "type": "image",
            "prefix_name": None,
            "label_color": None,
            "class_infor": None,
            "roi_list": None,
            "valid_exts": valid_exts,
        },
        "sub_data": {
            "Labelme_BBox": {
                "sub_path": label_sub_path,
                "type": "Labelme_BBox",
                "path": None,
                "prefix_name": "",
                "label_color": label_colors,
                "class_infor": class_info,
                "check_draw_objs": False,
                "draw_place_name": "base_data",
                "draw_roi_name": None,
            }
        },
    }
