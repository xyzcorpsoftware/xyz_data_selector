import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser(description="Review images and Labelme bbox labels.")
    parser.add_argument("--base-path", required=True, help="Dataset root path that contains images/ and bbox/.")
    parser.add_argument("--target", help="Session name for checkpoint/list files. Defaults to base folder name.")
    parser.add_argument("--save-path", help="Optional output root for captured images.")
    parser.add_argument("--image-sub-path", default="images", help="Image folder under base path.")
    parser.add_argument("--label-sub-path", default="bbox", help="Labelme bbox folder under base path.")
    parser.add_argument("--check-mode", default="pos", choices=["section", "excepted_section", "pos", "list"])
    parser.add_argument("--merging-axis", type=int, default=1, choices=[0, 1])
    return parser.parse_args()


def get_target_name(base_path, target):
    if target:
        return target
    return os.path.basename(os.path.normpath(base_path))


if __name__ == "__main__":
    args = parse_args()
    from common import data_player

    print("xzy data selector v0.1")

    obj_cls={"BG":0, "cup":1, "pedestrian":2}

    obj_color=[[0, 0, 0], [255, 0, 255], [255, 255, 0] ]


    file_config=    {
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

    base_path=args.base_path
    save_path=args.save_path
    target = get_target_name(base_path, args.target)
    file_config['base_data']['sub_path'] = args.image_sub_path
    file_config['sub_data']['Labelme_BBox']['sub_path'] = args.label_sub_path

    data1={
            target:
            {
                "base_path": base_path,
                "save_path": save_path,
                'play_data_type':"image", #[image, video]
                'check_mode':args.check_mode, #[section, pos]
                "check_point_path":None,
                "merging_axis":args.merging_axis,
                #"save_frame_gap":2,
                "base_data": file_config['base_data'],
                'sub_data': file_config['sub_data'],
            }

    }

    _config=data1
    _target_conifg = _config[target]

    print(target)
    player=data_player.Label_Player(_target_conifg, cmd_config=None, name=target)
    player.run_player()
