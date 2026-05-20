import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser(description="Split paired image/label files into task folders.")
    parser.add_argument("--base-path", required=True, help="Dataset root path that contains images/ and bbox/.")
    parser.add_argument("--out-path", help="Output task root. Defaults to base_path/task.")
    parser.add_argument("--item", default="1", help="Task item name.")
    parser.add_argument("--num-data", type=int, default=5, help="Number of image/label pairs per task folder.")
    parser.add_argument("--image-sub-path", default="images", help="Image folder under base path.")
    parser.add_argument("--label-sub-path", default="bbox", help="Labelme bbox folder under base path.")
    parser.add_argument("--valid-exts", default="jpg,png", help="Comma-separated image extensions.")
    parser.add_argument("--label-ext", default=".json", help="Label file extension.")
    parser.add_argument("--shuffle", action="store_true", help="Shuffle pairs before splitting.")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    from common.data_player import data_allocator

    print("a2z task data allocator")

    out_path = args.out_path or os.path.join(args.base_path, "task")
    item = args.item
    sample = {
        "items": [item],
        "out_path": out_path,
        "check_copy": True,
        item:
            {
                "num_data": args.num_data,
                "data_path": os.path.join(args.base_path, args.image_sub_path),
                "valid_exts": [ext.strip() for ext in args.valid_exts.split(",") if ext.strip()],
                "label_path": os.path.join(args.base_path, args.label_sub_path),
                "label_ext": args.label_ext,
                "shuffle": args.shuffle
            },
    }


    allocator=data_allocator(sample)
    allocator.run_task_allocating_v2()
