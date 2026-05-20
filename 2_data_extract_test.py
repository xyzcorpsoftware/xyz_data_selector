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
    parser.add_argument("--class-config", help="JSON file with classes and colors.")
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
    from common.app_config import build_file_config, load_class_config

    print("xyz data extractor")

    base_path=args.base_path
    file_list_pathname=args.file_list_pathname

    save_path=args.save_path
    target = get_target_name(base_path, args.target)
    class_info, label_colors = load_class_config(args.class_config)
    file_config = build_file_config(args.image_sub_path, args.label_sub_path, class_info, label_colors)

    data1 = {
        target:
            {
                "base_path": base_path,
                "save_path": save_path,
                'play_data_type': "image",  # [image, video]
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
