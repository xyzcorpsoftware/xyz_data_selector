#from  common import data_player
from collections import OrderedDict
from common import data_player


if __name__ == "__main__":

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

    base_path="C:/Project/dataset/20260514T080008Z-3-001"
    save_path=None
    data1={
            "20260514T080008Z-3-001":  # Front
            {
                "base_path": base_path,
                "save_path": save_path,
                'play_data_type':"image", #[image, video]
                'check_mode':"pos", #[section, pos]
                "check_point_path":None,
                "merging_axis":1,
                #"save_frame_gap":2,
                "base_data": file_config['base_data'],
                'sub_data': file_config['sub_data'],
            }
        
    }

    _config=data1
    target = "20260514T080008Z-3-001"
    _target_conifg = _config[target]

    print(target)
    player=data_player.Label_Player(_target_conifg, cmd_config=None, name=target)
    player.run_player()

    #conda install -c conda-forge opencv