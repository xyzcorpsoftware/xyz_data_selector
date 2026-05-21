import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser(description="Review images and Labelme bbox labels.")
    parser.add_argument("--base-path", required=True, help="Dataset root path that contains images/ and bbox/.")
    parser.add_argument("--target", help="Session name for checkpoint/list files. Defaults to base folder name.")
    parser.add_argument("--save-path", help="Optional output root for captured images.")
    parser.add_argument("--image-sub-path", default="images", help="Image folder under base path.")
    parser.add_argument("--label-sub-path", default="bbox", help="Labelme bbox folder under base path.")
    parser.add_argument("--valid-exts", default="jpg,gif,png,tga,jpeg,JPG,bmp", help="Comma-separated image extensions.")
    parser.add_argument("--class-config", help="JSON file with classes and colors.")
    parser.add_argument("--type-labels", help="JSON file mapping numeric check types to display labels.")
    parser.add_argument("--check-mode", default="pos", choices=["section", "excepted_section", "pos", "list"])
    parser.add_argument("--merging-axis", type=int, default=1, choices=[0, 1])
    parser.add_argument("--debug-keys", action="store_true", help="Print OpenCV key values and matched commands.")
    return parser.parse_args()


def get_target_name(base_path, target):
    if target:
        return target
    return os.path.basename(os.path.normpath(base_path))


if __name__ == "__main__":
    args = parse_args()
    from common import data_player
    from common.app_config import build_file_config, load_class_config, load_type_labels, parse_csv_list

    print("xyz data selector v0.1")

    base_path=args.base_path
    save_path=args.save_path
    target = get_target_name(base_path, args.target)
    class_info, label_colors = load_class_config(args.class_config)
    file_config = build_file_config(
        args.image_sub_path,
        args.label_sub_path,
        class_info,
        label_colors,
        valid_exts=parse_csv_list(args.valid_exts),
    )
    type_labels = load_type_labels(args.type_labels)
    cmd_config = {"type_text": type_labels} if type_labels is not None else None

    data1={
            target:
            {
                "base_path": base_path,
                "save_path": save_path,
                'play_data_type':"image", #[image, video]
                'check_mode':args.check_mode, #[section, pos]
                "check_point_path":None,
                "merging_axis":args.merging_axis,
                "debug_keys": args.debug_keys,
                #"save_frame_gap":2,
                "base_data": file_config['base_data'],
                'sub_data': file_config['sub_data'],
            }

    }

    _config=data1
    _target_conifg = _config[target]

    print(target)
    player=data_player.Label_Player(_target_conifg, cmd_config=cmd_config, name=target)
    player.run_player()
