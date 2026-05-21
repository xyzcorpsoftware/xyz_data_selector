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
    parser.add_argument("--reset-checkpoint", action="store_true", help="Start from frame 0 and ignore saved checkpoint.")
    parser.add_argument("--sessions", action="store_true", help="Treat base path as a folder that contains session folders.")
    return parser.parse_args()


def get_target_name(base_path, target):
    if target:
        return target
    return os.path.basename(os.path.normpath(base_path))


def find_session_paths(base_path, image_sub_path, label_sub_path):
    sessions = []
    for name in sorted(os.listdir(base_path)):
        path = os.path.join(base_path, name)
        if not os.path.isdir(path):
            continue
        if os.path.isdir(os.path.join(path, image_sub_path)) and os.path.isdir(os.path.join(path, label_sub_path)):
            sessions.append(path)
    return sessions


def run_selector(args, base_path, session_index=None, session_count=None):
    from common import data_player
    from common.app_config import build_file_config, load_class_config, load_type_labels, parse_csv_list

    save_path = args.save_path
    target = get_target_name(base_path, None if args.sessions else args.target)
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
                "reset_checkpoint": args.reset_checkpoint,
                #"save_frame_gap":2,
                "base_data": file_config['base_data'],
                'sub_data': file_config['sub_data'],
            }

    }

    _config=data1
    _target_conifg = _config[target]

    if session_index is not None:
        print("[%d/%d] %s" % (session_index, session_count, target))
    else:
        print(target)
    player=data_player.Label_Player(_target_conifg, cmd_config=cmd_config, name=target)
    player.run_player()


if __name__ == "__main__":
    args = parse_args()

    print("xyz data selector v0.1")

    if args.sessions:
        session_paths = find_session_paths(args.base_path, args.image_sub_path, args.label_sub_path)
        if len(session_paths) == 0:
            raise SystemExit("No session folders found under: %s" % args.base_path)
        print("Found %d sessions." % len(session_paths))
        for idx, session_path in enumerate(session_paths, start=1):
            run_selector(args, session_path, session_index=idx, session_count=len(session_paths))
    else:
        run_selector(args, args.base_path)
