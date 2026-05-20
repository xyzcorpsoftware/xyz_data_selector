from common import data_player
from collections import OrderedDict
import os

if __name__ == '__main__':
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
    base_path="C:/Project/dataset/20260514T080008Z-3-001"
    file_list_pathname=None

    save_path=None

    for key in file_config['sub_data'].keys():
        file_config['sub_data'][key]['path']=None


    #class에 입력될 데이터
    #['image'
    data1 = {
        "20260514T080008Z-3-001":  # Front
            {
                "base_path": base_path,
                "save_path": save_path,
                'play_data_type': "image",  # [image, video, a2z_video]
                "file_list_pathname":file_list_pathname,
                'check_mode': "list",  # [pos, list]
                "base_data": file_config['base_data'],
                'sub_data': file_config['sub_data'],
                'check_copy':True,
                'data_merging':False,                   #merging same folder for different data_type such as 0,1, 2, 3
                'check_same_folder':True                #save data in same folder for label and image
            }
    }


    _config = data1
    target = "20260514T080008Z-3-001"

    Extractor=data_player.Data_Extractor(_config[target], name=target)
    Extractor.run()
