import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser(description="Extract checked image/label files.")
    parser.add_argument("--base-path", required=True, help="Dataset root path that contains images/ and bbox/.")
    parser.add_argument("--target", help="Session name used in saved check-list files. Defaults to base folder name.")
    parser.add_argument("--save-path", help="Output path. Defaults to base_path/target.")
    parser.add_argument("--file-list-pathname", help="Explicit check-list file path to read.")
    parser.add_argument("--image-sub-path", default="images", help="Image folder under base path.")
    parser.add_argument("--label-sub-path", default="bbox", help="Labelme bbox folder under base path.")
    parser.add_argument("--check-mode", default="list", choices=["pos", "list"])
    parser.add_argument("--move", action="store_true", help="Move files instead of copying them.")
    parser.add_argument("--data-merging", action="store_true", help="Merge output into the same folder by type.")
    parser.add_argument("--separate-folders", action="store_true", help="Save image and label files into subfolders.")
    return parser.parse_args()


def get_target_name(base_path, target):
    if target:
        return target
    return os.path.basename(os.path.normpath(base_path))

if __name__ == '__main__':
    args = parse_args()
    from common import data_player

    print("xyz data extractor")

    obj_cls = {"BG": 0, "cup": 1, "pedestrian": 2}
    obj_color = [[0, 0, 0], [255, 0, 255], [255, 255, 0]]


    file_config={
         'base_data':
            {
                "sub_path": "images",
                "type": "image",
                "prefix_name": None,
                "label_color": None,
                "class_infor": None,
                "roi_list": None,#to do list

            },
         'sub_data':
            {
                "Labelme_BBox":
                {
                    "sub_path": "bbox",
                    "type": "Labelme_BBox",
                    "path": None,
                    "prefix_name": "",
                    "label_color": obj_color,
                    "class_infor": obj_cls,
                    'check_draw_objs':False,
                    "draw_place_name": "base_data",
                    "draw_roi_name":None


                }

        }

    }

    #다이얼로그에서 읽어올 파라미터
    base_path=args.base_path
    file_list_pathname=args.file_list_pathname

    save_path=args.save_path
    target = get_target_name(base_path, args.target)
    file_config['base_data']['sub_path'] = args.image_sub_path
    file_config['sub_data']['Labelme_BBox']['sub_path'] = args.label_sub_path

    for key in file_config['sub_data'].keys():
        file_config['sub_data'][key]['path']=None


    #class에 입력될 데이터
    #['image'
    data1 = {
        target:
            {
                "base_path": base_path,
                "save_path": save_path,
                'play_data_type': "image",  # [image, video, a2z_video]
                "file_list_pathname":file_list_pathname,
                'check_mode': args.check_mode,  # [pos, list]
                "base_data": file_config['base_data'],
                'sub_data': file_config['sub_data'],
                'check_copy': not args.move,
                'data_merging': args.data_merging,
                'check_same_folder': not args.separate_folders
            }
    }


    _config = data1

    Extractor=data_player.Data_Extractor(_config[target], name=target)
    Extractor.run()
