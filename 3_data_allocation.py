from collections import OrderedDict
import os
from common.data_player import data_allocator

if __name__ == '__main__':
    print("a2z task data allocator")

    sample = {
        "items": ["1"],
        "out_path": "C:/Project/dataset/20260514T080008Z-3-001/task",
        "check_copy": True,
        "1":
            {
                "num_data": 5,
                "data_path": "C:/Project/dataset/20260514T080008Z-3-001/images",
                "valid_exts": ["jpg", "png"],
                "label_path": "C:/Project/dataset/20260514T080008Z-3-001/bbox",
                "label_ext": ".json",
                "shuffle": False
            },
    }


    allocator=data_allocator(sample)
    allocator.run_task_allocating_v2()
