import os
import time

import numpy as np
import cv2
import json
import threading
import concurrent.futures
import json
import shutil
import multiprocessing
from functools import partial
import tqdm


from common.data_structure import *
from common import data_loader as loader
from common import data_draw as drawer
def check_key_value(config, key):
    if key in config:
        if config[key] ==None:
            return False
        else:
            return True

    return False

class Type_list:
    def __init__(self, config=None):
        self._txt_type_list = ['Kitti_BBox']
        self._json_type_list = ['Labelme_BBox', 'Labelme_Line', 'Labelme_Region']
        self._bbox_list = ['Labelme_BBox']

        self._image_type_list = ['image', 'id_map', 'color_map','xyz_image']
        self._video_type_list = ['video']
        self._play_type_list = ['index_image', 'image', 'video']


        self._check_mode_list = ['section', "excepted_section", "pos", "list"]
        self._section_mode_list = ["section", "excepted_section"]
        self._file_keys = {"section": ['target', 'section', 'file', 'type'], "pos": ['file', 'type'],
                          "list": ["file"]}

        self._check_list_sub_filename=\
        {
            "list":"_base_check_file_list.txt",
            "section":"_section_file_list.txt",
            "excepted_section":"_excepted_section_file_list.txt",
            "pos":"_check_file_list.txt"
        }


class Operation_Key:
    def __init__(self, key_path=None):
        self.prev = ord('a')
        self.next = ord('d')
        self.skip_prev = ord('f')
        self.skip_next = ord('h')
        self.skip_frame = 10

        self.zoom_in = ord('z')
        self.zoom_out = ord('c')
        self.zoom_ratio = 0.05

        self.section_start = ord('q')
        self.section_end = ord('e')
        self.del_section = ord('w')

        self.save_file_list = ord('p')

        self.types = [ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9')]
        self._type_list = [1, 2, 3, 4, 5, 6, 7, 8]
        self.type_color = {1: [255, 127, 80], 2: [0, 255, 127], 3: [0, 255, 255], 4: [0, 191, 255], 5: [139, 0, 139],
                           6: [255, 0, 255], 7: [255, 20, 147],
                           8: [255, 228, 196], 9: [255, 228, 181], 0: [0, 0, 255]}
        self.run_continue_play = 32  # spacebar
        self.exit = 27
        self.capture = ord('t')
        self._basic_check = ord('s')  # default type 0

        self.show_msg = ord('m')
        self.update_trackbar = ord('/')

        self.inc_draw_thick = ord('>')
        self.dec_draw_thick = ord('<')
        self.inc_font_scale = ord('}')
        self.dec_font_scale = ord('{')

        self.max_thick = 3
        self.min_thick = 1
        self.max_fontscale = 3
        self.min_fontscale = 0.4

        self._type_text = {1: "scene1", 2: "scene2", 3: "scene3", 4: "scene4", 5: "scene5",
                           6: "scene6", 7: "scene7", 8: "None", 9: "None"}
        # self._basic_check = ord['b']

        self.zoom_min_ratio = 0.4
        self.zoom_max_ratio = 1.6

    def set_key_config(self, config):

        if check_key_value(config, 'prev'):
            self.prev = ord(config['prev'])

        if check_key_value(config, 'next'):
            self.next = ord(config['next'])

        if check_key_value(config, 'skip_prev'):
            self.skip_prev = ord(config['skip_prev'])

        if check_key_value(config, 'skip_next'):
            self.skip_next = ord(config['skip_next'])

        if check_key_value(config, 'skip_frame'):
            self.skip_frame = config['skip_frame']

        if check_key_value(config, 'zoom_in'):
            self.zoom_in = ord(config['zoom_in'])

        if check_key_value(config, 'zoom_out'):
            self.zoom_out = ord(config['zoom_out'])

        if check_key_value(config, 'zoom_ratio'):
            self.zoom_ratio = config['zoom_ratio']

        if check_key_value(config, 'section_start'):
            self.section_start = ord(config['section_start'])

        if check_key_value(config, 'section_end'):
            self.section_end = ord(config['section_end'])
        if check_key_value(config, 'del_section'):
            self.del_section = ord(config['del_section'])
        if check_key_value(config, 'save_file_list'):
            self.save_file_list = ord(config['save_file_list'])
        if check_key_value(config, 'types'):
            self.types = []
            for type in config['types']:
                self.types.append(ord(type))

        if check_key_value(config, '_type_list'):
            self._type_list = config['_type_list']

        if check_key_value(config, 'type_color'):
            self.type_color = {}
            for type_ in config['type_color'].keys():
                self.type_color[int(type_)] = config['type_color'][type_]

        if check_key_value(config, 'run_continue_play'):
            self.run_continue_play = config['run_continue_play']

        if check_key_value(config, 'exit'):
            self.exit = config['exit']

        if check_key_value(config, 'capture'):
            self.capture = ord(config['capture'])

        if check_key_value(config, '_basic_check'):
            self._basic_check = ord(config['_basic_check'])

        if check_key_value(config, 'type_text'):
            self._type_text = config['type_text']
            self._type_text = {int(k): v for k, v in self._type_text.items()}

        if check_key_value(config, 'zoom_min_ratio'):
            self.zoom_min_ratio = config['zoom_min_ratio']
        if check_key_value(config, 'zoom_max_ratio'):
            self.zoom_max_ratio = config['zoom_max_ratio']

        if check_key_value(config, 'show_msg'):
            self.show_msg = ord(config['show_msg'])
        if check_key_value(config, 'update_trackbar'):
            self.update_trackbar = ord(config['update_trackbar'])

        if check_key_value(config, 'inc_draw_thick'):
            self.inc_draw_thick = ord(config['inc_draw_thick'])
        if check_key_value(config, 'dec_draw_thick'):
            self.dec_draw_thick = ord(config['dec_draw_thick'])
        if check_key_value(config, 'inc_font_scale'):
            self.inc_font_scale = ord(config['inc_font_scale'])
        if check_key_value(config, 'dec_font_scale'):
            self.dec_font_scale = ord(config['dec_font_scale'])

        if check_key_value(config, 'max_thick'):
            self.max_thick = config['max_thick']
        if check_key_value(config, 'min_thick'):
            self.min_thick = config['min_thick']
        if check_key_value(config, 'max_fontscale'):
            self.max_fontscale = config['max_fontscale']
        if check_key_value(config, 'min_fontscale'):
            self.min_fontscale = config['min_fontscale']

    def get_key_type(self, cmd):
        return self._type_list[self.types.index(cmd)]

    def get_type_color(self, pos_type):
        return self.type_color[pos_type]

    def get_base_check_color(self):
        return self._basic_check_color

def open_file_list(data_path, data_type='image'):
    if data_type == 'image':
        valid_exts = ["jpg", "gif", "png", "tga", "jpeg", "JPG", "bmp"]
        data_lists = loader.get_files_from_folder(data_path, valid_exts=valid_exts, check_list=True)
        num_frames = len(data_lists)
        print(data_path)
        return data_lists, num_frames

    return None,0

#file 정보
class File_infor:
    def __init__(self, base_path, config):

        type_list = Type_list()
        self._image_type_list = type_list._image_type_list
        self._txt_type_list = type_list._txt_type_list
        self._json_type_list = type_list._json_type_list
        self._bbox_list = type_list._bbox_list
        self.check_list_sub_filename = type_list._check_list_sub_filename

        self.image = None
        self.data = None

        self.data_path = None
        self.data_type = None
        self.prefix = None
        self.label_color = None
        self.class_infor = None
        #self.draw_obj = False
        #self.draw_baseline = False
        self.sub_path = None
        self.file_ext = None

        self.targe_img_roi = None  # None: Origin_Imagee, rect
        self.base_size = None  # None: Origion_Image
        self.draw_place_name = None  # the place draw data

        self.set_config(base_path, config)

    def set_config(self, base_path, config):
        self.data_path = base_path
        self.image = None
        self.data = None

        self.data_type = None
        self.prefix = None
        self.label_color = None
        self.class_infor = None
        #self.draw_obj = False
        #self.draw_baseline = False
        #self.roi_dict = None
        self.sub_path = None
        self.draw_place_name = None  # the place draw data

        self.base_size = None  # None: Origion_Image
        # self.targe_img_roi = None  # None: Origin_Imagee, rect
        #self.draw_place_name = None  # the place draw data
        #self.draw_roi_name = None  # drawing roi region

        if check_key_value(config, 'sub_path'):
            self.data_path = os.path.join(base_path, config['sub_path'])
            self.sub_path = config['sub_path']

        if check_key_value(config, 'type'):
            self.data_type = config['type']

        if check_key_value(config, 'prefix_name'):
            self.prefix = config['prefix_name']

        if check_key_value(config, 'class_infor'):
            self.class_infor = config['class_infor']
        if check_key_value(config, 'label_color'):
            self.label_color = config['label_color']
        if check_key_value(config, 'draw_place_name'):
            self.draw_place_name = config['draw_place_name']


        #if check_key_value(config, 'roi'):
        #    _roi_dict = config['roi']
        #    self.roi_dict = self.get_roi_dics(_roi_dict)

        #if check_key_value(config, 'check_draw_objs'):
        #    self.draw_obj = config['check_draw_objs']

        #if check_key_value(config, 'draw_roi_name'):
        #    self.draw_roi_name = config['draw_roi_name']

        if check_key_value(config, 'base_size'):
            self.base_size = config['base_size']

        self._file_ext = self.get_target_ext(self.data_type)
        if check_key_value(config, 'file_ext'):
            self._file_ext = config['file_ext']

    def get_check_list_save_pathname(self, mode, file_name=None, base_path=None):
        _path_name = None

        if mode in self.check_list_sub_filename:
            _path_name = self.check_list_sub_filename[mode]
            if file_name is not None:
                _path_name = file_name + _path_name
            if base_path is not None:
                _path_name = os.path.join(base_path, _path_name)

        return _path_name

    def get_target_ext(self, data_type):
        if data_type in self._txt_type_list:
            return '.txt'
        elif data_type in self._json_type_list:
            return '.json'
        return None

    def load_data(self, file_name, target_prefix=None,  image=None):
        self.image = None
        self.data = None
        _data_name = file_name
        if self.data_type in self._image_type_list:
            if check_value(image) and check_value(file_name):
                self.image = image
            else:
                _data_pathname = loader.get_target_file_name(file_name, target_prefix, self.prefix, data_path=self.data_path)
                # _data_pathname = os.path.join(self.data_path, _data_name)
                self.image = cv2.imread(_data_pathname)

            #if self.data_type == 'id_map':

        else:
            _data_pathname = loader.get_target_file_name(file_name, target_prefix, self.prefix, data_path=self.data_path,
                                                change_ext=self._file_ext)
            print(_data_pathname,self.data_type)
            self.data = loader.Open_Label_Data(self.data_type, _data_pathname, self.class_infor, self.label_color)

    def draw_data(self, image, roi=None, check_msg=False, thick=1, draw_font=1):
        if image is not None:
            if self.data_type in self._bbox_list:
                drawer.draw_bbox(image, self.data, base_size=self.base_size, roi_rect=roi, color_list=self.label_color,
                          check_msg=check_msg, thick=thick, draw_font=draw_font)



class Player_Base:
    def __init__(self, name, cmd_config):
        type_list = Type_list()
        self._image_type_list = type_list._image_type_list
        self._video_type_list = type_list._video_type_list
        self._play_type_list = type_list._play_type_list

        #checked file list
        self._check_file_dict = Check_Name_Dict()
        self._basic_check_dict = Check_Name_Dict()



        self.show_msg = True
        self.draw_thick = 1
        self.draw_font = 0.5

        #operation key setting
        self._op_key = Operation_Key()
        if cmd_config is not None:
            self._op_key.set_key_config(cmd_config)


        self._play_data_type = 'image'  # ['image', 'video']
        self._img_merging_axis = 1  # 0:y축, 1:축, 3:융합(to do list)

        self._view_size = [720, 640, 3]

        self._rescale_ratio_height = 1.
        self._rescale_ratio_width = 1.
        self._data_list = None
        self._num_total_frames = 0
        self._current_frame = 0
        self._view_image = 0
        self._in_data_dict = None
        self._window_name = name  # os.path.split(self._data_path_lists[0])[1]
        self._frame_name = None

        self._check_continue = False
        self._resize_ratio_width = 1.
        self._resize_ratio_height = 1.
        self._pos_bar_height = 15

        self._section_start_pos = None
        self._section_end_pos = None
        self._check_mode = 'section'  # 'section', 'point'
        # path infor
        self._base_path = None
        self._data_pathname=None

        self._check_point_path = None
        self._capture_save_path = None
        self._file_infors = None


        self._holding_check=False #holding checking button when operating schroll
        self._check_point_pathname = None
        self.save_frame_gap=1

    def get_base_path(self, base_pathname, play_data_type):
        if play_data_type in self._image_type_list:
            return base_pathname
        elif play_data_type in self._video_type_list:
            return os.path.dirname(base_pathname)

    def get_window_name(self, name, play_type, data_path):
        if check_str_value(name):
            return name
        else:
            if play_type in self._image_type_list:
                return fl.get_sub_folder(data_path)
            else:
                _name=os.path.basename(data_path)
                return os.path.splitext(_name)[0]

    def set_file_configs(self, config, main_file_config, sub_file_config, name):

        self._holding_check = False
        if check_key_value(config, 'play_data_type'):
            self._play_data_type = config['play_data_type']

        self._data_pathname = config['base_path']
        self._base_path = self.get_base_path(self._data_pathname, self._play_data_type)
        self._check_point_path = self._base_path

        self.window_name = self.get_window_name(name, self._play_data_type, self._data_pathname)

        if check_key_value(config, 'check_point_path'):
            self._check_point_path = config['check_point_path']
            loader.make_folder(self._check_point_path)

        self._capture_save_path = os.path.join(self._base_path, self.window_name + '_capture')

        if check_key_value(config, 'save_path'):
            self._capture_save_path = os.path.join(config['save_path'], self.window_name + '_capture')

        self._check_point_pathname = os.path.join(self._check_point_path, self.window_name + "_check_point.json")

        self._file_infors = OrderedDict()
        self._file_infors['base_data'] = File_infor(self._base_path, main_file_config)
        self._file_infors['sub_data'] = OrderedDict()

        for key, _conf in sub_file_config.items():
            if check_key_value(_conf, 'path'):
                base_path = _conf['path']
            else:
                base_path = self._base_path
            self._file_infors['sub_data'][key] = File_infor(base_path, _conf)

        if check_key_value(config, 'merging_axis'):
            self._img_merging_axis = config['merging_axis']

        if check_key_value(config, 'check_mode'):
            self._check_mode = config['check_mode']

        if check_key_value(config, "save_frame_gap"):
            self.save_frame_gap = config['save_frame_gap']

    def open_check_point(self, data_pathname, total_num_data=None):
        self._resize_ratio_width = 1.
        self._resize_ratio_height = 1.
        self._current_frame = 0

        self._check_file_dict.clear()
        self._check.clear()

        if os.path.isfile(data_pathname):
            data = json.load(open(data_pathname, 'r'))
            if data is not None:
                self._current_frame = data['current_pos']
                self._current_frame = max(0, self._current_frame)
                if total_num_data is not None:
                    self._current_frame = min(total_num_data - 1, self._current_frame)

                self._resize_ratio_width = data['resize_ratio_width']
                self._resize_ratio_height = data['resize_ratio_height']
                if check_key_value(data, 'section_list'):
                    for _item in data['section_list']:
                        self._sections.add_item_dict(_item)
                if check_key_value(data, 'basic_check_lists'):
                    for _item in data['basic_check_lists']:
                        self._basic_check_dict.add(_item['name'], _item['pos'], _item['type'])
                if check_key_value(data, 'check_lists'):
                    for _item in data['check_lists']:
                        self._check_name_dict.add(_item['name'], _item['pos'], _item['type'])

    def get_window_name(self, name, play_type, data_path):
        if check_str_value(name):
            return name
        else:
            if play_type in self._image_type_list:
                return loader.get_sub_folder(data_path)
            else:
                _name=os.path.basename(data_path)
                return os.path.splitext(_name)[0]

    def create_window(self, w, h, name, current_pos, total_frame, callback_function):
        cv2.destroyAllWindows()
        cv2.namedWindow(name)
        cv2.resizeWindow(name, w, h)
        cv2.createTrackbar('frame', name, 0, total_frame - 1, callback_function)
        cv2.setTrackbarPos('frame', name, current_pos)

    def get_pose_bar_image(self, current_frame, total_frame, width, height=15):
        bar = np.zeros([height, width, 3], dtype=np.uint8)

        if current_frame == 0:
            now_pos = 0
        else:
            now_pos = int(current_frame / total_frame * width)

        #if self._check_mode == 'section':
        #    self._sections.draw_section_pos_bar_image(bar, total_frame, self._op_key.type_color)
        bar = self._basic_check_dict.set_color_bar_image(bar, total_frame, width, self._op_key.type_color)
        if self._check_mode == "pos":
            bar = self._check_file_dict.set_color_bar_image(bar, total_frame, width, self._op_key.type_color)

        # for range in self._basic_check_dict.

        bar[:, now_pos] = [0, 255, 0]
        return bar

    def open_check_point(self, data_pathname, total_num_data=None):
        self._resize_ratio_width = 1.
        self._resize_ratio_height = 1.
        self._current_frame = 0

        self._check_file_dict.clear()
        self._basic_check_dict.clear()

        if os.path.isfile(data_pathname):
            data = json.load(open(data_pathname, 'r'))
            if data is not None:
                self._current_frame = data['current_pos']
                self._current_frame = max(0, self._current_frame)
                if total_num_data is not None:
                    self._current_frame = min(total_num_data - 1, self._current_frame)

                self._resize_ratio_width = data['resize_ratio_width']
                self._resize_ratio_height = data['resize_ratio_height']
                #if check_key_value(data, 'section_list'):
                # todo list

                if check_key_value(data, 'basic_check_lists'):
                    for _item in data['basic_check_lists']:
                        self._basic_check_dict.add(_item['name'], _item['pos'], _item['type'])
                if check_key_value(data, 'check_lists'):
                    for _item in data['check_lists']:
                        self._check_file_dict.add(_item['name'], _item['pos'], _item['type'])

    def save_check_point(self, data_pathname):
        data = OrderedDict()
        data['total_frame'] = self._num_total_frames
        data['current_pos'] = self._current_frame
        data['resize_ratio_width'] = self._resize_ratio_width
        data['resize_ratio_height'] = self._resize_ratio_height


        data['basic_check_lists'] = []
        for key, value in self._basic_check_dict._check_names.items():
            _lists = OrderedDict()
            _lists['pos'] = value['pos']
            _lists['name'] = key
            _lists['type'] = value['type']
            data['basic_check_lists'].append(_lists)

        data['check_lists'] = []
        for key, value in self._check_file_dict._check_names.items():
            _lists1 = OrderedDict()
            _lists1['pos'] = value['pos']
            _lists1['name'] = key
            _lists1['type'] = value['type']
            data['check_lists'].append(_lists1)

        json.dump(data, open(data_pathname, 'w'))

    def check_video(self):
        if self._play_data_type in self._video_type_list:
            return 1
        return 0

    def open_play_data_set(self, check_sorting=True):
        self._current_frame = 0
        self._check_file_dict.clear()
        self._basic_check_dict.clear()

        self._data_list = None

        if self._play_data_type in self._image_type_list:
            self._data_list, self._num_total_frames = open_file_list(self._file_infors['base_data'].data_path,
                                                                self._file_infors['base_data'].data_type)
            # print("test", os.path.splitext(self._data_list[0])[0].split('_')[-1])
            print("#Loading data %d"%(self._num_total_frames))
            if check_sorting:
                if self._play_data_type == 'index_image':
                    self._data_list = sorted(self._data_list,
                                             key=lambda x: tuple(map(int, os.path.splitext(x)[0].split('_')[-1])))

        #elif self._play_data_type in self._video_type_list:
        #    self._data_list = Video(self._data_pathname, self._play_data_type, config=None)
        #    self._num_total_frames = self._data_list.num_total_frame

        self.open_check_point(self._check_point_pathname, self._num_total_frames)

    def get_frame_data(self, pos, total_frame):
        _data = OrderedDict()
        file_name = None

        if pos >= 0 and pos < total_frame:
            base_infor = self._file_infors['base_data']
            sub_infor = self._file_infors['sub_data']

            if self._play_data_type in self._image_type_list:
                file_name = self._data_list[pos]
                # base_data load
                base_infor.load_data(file_name)

                # sub_data_infor
                for key, infor in sub_infor.items():
                    infor.load_data(file_name, target_prefix=base_infor.prefix)

                self.draw_image_data(base_infor, sub_infor)
            #elif self._play_data_type in self._video_type_list:
            #    file_name, _image = self._data_list.get_frame(pos, name=self.window_name)
            #    base_infor.load_data(file_name, draw_object=draw_object, image=_image)
            #    for key, infor in sub_infor.items():
            #        infor.load_data(file_name, target_prefix=base_infor.prefix, draw_object=draw_object)

        return file_name

    def draw_image_data(self, base_infor, sub_infor):
        _image = None
        for key, infor in sub_infor.items():
            if infor.draw_place_name is not None:
                if infor.draw_place_name == 'base_data':
                    target_infor = base_infor
                else:
                    target_infor = sub_infor[infor.draw_place_name]
                _image = target_infor.image

                infor.draw_data(_image, roi=None, check_msg=self.show_msg, thick=self.draw_thick,
                                draw_font=self.draw_font)

    def draw_check_point_text(self, image, file_name, frame_pos, draw_y_pos, add_offset=20, fontScale=0.5, thick=2):
        y_pos = draw_y_pos
        _pos, _type = self._basic_check_dict.get_pos_type(file_name)
        if _pos >= 0:
            y_pos += add_offset
            text = "[%d]Basic" % (_pos)
            cv2.putText(image, text, (0, y_pos), cv2.FONT_HERSHEY_SIMPLEX, fontScale, self._op_key.type_color[_type],
                        thick)
        if self._check_mode == 'pos':
            _pos, _type = self._check_file_dict.get_pos_type(file_name)
            if _type >= 0:
                y_pos += add_offset
                text = "[%d:%s]Check" % (_pos, self._op_key._type_text[_type])
                cv2.putText(image, text, (0, y_pos), cv2.FONT_HERSHEY_SIMPLEX, fontScale,
                            self._op_key.type_color[_type], thick)
        return y_pos

    def get_view_image(self, file_name, base_infor, sub_infor, current_frame, total_frame, merge_axis=1, fontScale=0.5,
                       thick=2):

        imgs = []
        view_img = None
        if base_infor.image is not None:
            _base_image = base_infor.image.copy()
            y_pos = 20
            msg = "[%d/%d] %s" % (current_frame, total_frame, file_name)
            cv2.putText(_base_image, msg, (0, y_pos), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (255, 0, 0), thick)
            y_pos = self.draw_check_point_text(_base_image, file_name, current_frame, y_pos, fontScale=fontScale,
                                               thick=thick)

            if self._resize_ratio_height != 1.0 or self._resize_ratio_width != 1.0:
                imgs.append(
                    cv2.resize(_base_image, None, fx=self._resize_ratio_width, fy=self._resize_ratio_height))
            else:
                imgs.append(_base_image)

            for key, infor in sub_infor.items():
                if infor.image is not None:
                    if self._resize_ratio_height != 1.0 or self._resize_ratio_width != 1.0:
                        imgs.append(
                            cv2.resize(infor.image, None, fx=self._resize_ratio_width, fy=self._resize_ratio_height))
                    else:
                        imgs.append(infor.image)
            if len(imgs) > 0:
                view_img = np.concatenate(imgs, axis=merge_axis)
                height, width = view_img.shape[:2]
                pos_bar = self.get_pose_bar_image(current_frame, total_frame, width=width, height=self._pos_bar_height)
                view_img = np.concatenate([pos_bar, view_img], axis=0)

        return view_img

    def save_checked_file_list_data(self, infor, name, num_zero=6, frame_gap=1):
        check_video=False
        base_check_file_path =infor.get_check_list_save_pathname('list', file_name=self.window_name, base_path=self._check_point_path )
        loader.save_checked_pos_file_dict(base_check_file_path, self._basic_check_dict, check_type=False)
        check_file_list_path=infor.get_check_list_save_pathname("pos", file_name=self.window_name, base_path=self._check_point_path)
        loader.save_checked_pos_file_dict(check_file_list_path,self._check_file_dict)

    def save_capture_image(self, file_name, save_path, img, pos=0, check_mode="pos"):
        if check_value(img):
            loader.make_folder(save_path)
            _name = os.path.splitext(file_name)[0]

            _check_type = 0
            if check_mode == "pos":
                _check_type = self._check_file_dict.get_type(file_name)
            if _check_type > 0:
                _name = "%s_%s" % (self._op_key._type_text[_check_type], _name)

            save_pathname = os.path.join(save_path, _name + '.png')

            cv2.imwrite(save_pathname, img)
    def set_next_frame_number(self, total_frame, add_value):
        self._previous_frame = self._current_frame
        self._current_frame += add_value

        if self._current_frame <= 0:
            self._current_frame = 0
            self._previous_frame = -1
        elif self._current_frame >= total_frame - 1:
            self._current_frame = total_frame - 1
            self._previous_frame = total_frame - 2

    def next_data_command(self, cmd, file_name):
        if cmd == self._op_key.run_continue_play:
            if self._check_continue == True:
                self._check_continue = False
                # self._check_set_trackbar = False
            else:
                self._check_continue = True
                # self._check_set_trackbar = True
            return 1
        if cmd == self._op_key.exit:
            cv2.destroyAllWindows()
            return -1
        if cmd == self._op_key.prev:
            self.set_next_frame_number(self._num_total_frames, -1)
            cv2.waitKey(1)
            return 1
        if cmd == self._op_key.next:
            self.set_next_frame_number(self._num_total_frames, 1)
            cv2.waitKey(1)
            return 1
        if cmd == self._op_key.skip_next:
            self.set_next_frame_number(self._num_total_frames, self._op_key.skip_frame)
            cv2.waitKey(1)
            return 1
        if cmd == self._op_key.skip_prev:
            self.set_next_frame_number(self._num_total_frames, -self._op_key.skip_frame)
            cv2.waitKey(1)
            return 1

        if cmd == self._op_key.zoom_in:
            self._resize_ratio_width += self._op_key.zoom_ratio
            self._resize_ratio_height += self._op_key.zoom_ratio
            self._resize_ratio_width = min(self._op_key.zoom_max_ratio, self._resize_ratio_width)
            self._resize_ratio_height = min(self._op_key.zoom_max_ratio, self._resize_ratio_height)
            return 1
        if cmd == self._op_key.zoom_out:
            self._resize_ratio_width -= self._op_key.zoom_ratio
            self._resize_ratio_height -= self._op_key.zoom_ratio
            self._resize_ratio_width = max(self._op_key.zoom_min_ratio, self._resize_ratio_width)
            self._resize_ratio_height = max(self._op_key.zoom_min_ratio, self._resize_ratio_height)
            return 1


        if cmd in self._op_key.types:
            if self._check_mode == 'pos':
                _type = self._op_key.get_key_type(cmd)
                self._check_file_dict.add_modify_del_by_name(file_name, self._current_frame, _type)
            return 1
        if cmd == self._op_key._basic_check:
            self._basic_check_dict.add_modify_del_by_name(file_name, self._current_frame, check_del=True)
            return 1

        if cmd == self._op_key.del_section:
            if self._check_mode == 'pos':
                self._check_file_dict.del_by_name(file_name)
            return 1

        if cmd == self._op_key.update_trackbar:
            if self._check_set_trackbar == False:
                self._check_set_trackbar = True
            else:
                self._check_set_trackbar = False
            return 1

        if cmd == self._op_key.save_file_list:
            self.save_checked_file_list_data(self._file_infors['base_data'], self.window_name,
                                             frame_gap=self.save_frame_gap)
            return 1

        if cmd == self._op_key.capture:
            return 2

        if cmd == self._op_key.show_msg:
            if self.show_msg:
                self.show_msg = False
            else:
                self.show_msg = True
            return 1
        if cmd == self._op_key.inc_draw_thick:
            self.draw_thick = min(self._op_key.max_thick, self.draw_thick + 1)
            return 1
        if cmd == self._op_key.dec_draw_thick:
            self.draw_thick = max(self._op_key.min_thick, self.draw_thick - 1)
            return 1
        if cmd == self._op_key.inc_font_scale:
            self.draw_font = min(self._op_key.max_fontscale, self.draw_font + 0.1)
            return 1
        if cmd == self._op_key.dec_font_scale:
            self.draw_font = max(self._op_key.min_fontscale, self.draw_font - 0.1)
            return 1

        return 0

class Label_Player(Player_Base):
    def __init__(self, config, cmd_config, name=None):
        super(Label_Player, self).__init__(name, cmd_config)
        self._previous_frame = -1
        self.view_image = None
        self.set_config(config, name)

    def set_config(self, config, name):
        if check_key_value(config, 'base_data'):
            base_data_conf = config['base_data']
        else:
            base_data_conf = \
                {
                    "sub_path": "images",
                    "type": "image",
                    "prefix_name": None,
                    "label_color": None,
                    "class_infor": None,
                    'check_draw_objs': False
                }
        if check_key_value(config, 'sub_data'):
            sub_data_conf = config['sub_data']
        else:
            sub_data_conf = \
                {
                    "label": {
                        "sub_path": "bbox",
                        "type": "Labelme_BBox",
                        "prefix_name": "Output",
                        "label_color": [[0, 0, 0], [255, 255, 255], [0, 255, 255], [0, 0, 255], [0, 255, 0],
                                        [102, 102, 255]],
                        "class_infor": {"BG": 0, "cup": 1, "person": 2},
                        'check_draw_objs': False,
                        "draw_place_name": None,
                        "base_size": None

                    }
                }

        self.set_file_configs(config, base_data_conf, sub_data_conf, name)
        print("test")

    def check_file_load(self):
        if self._current_frame != self._previous_frame:
            return 1
        return 0

    def run_trackbar_frame(self, val):
        self._current_frame = val
        if self.check_file_load():
            self._frame_name = self.get_frame_data(self._current_frame, self._num_total_frames )
        self.show_data()

    def init_player_window(self, total_frame, current_frame):
        self._frame_name = None
        base_infor = self._file_infors['base_data']
        sub_infor = self._file_infors['sub_data']
        if total_frame > 0:
            self._frame_name = self.get_frame_data(current_frame, total_frame)
            self.view_image = self.get_view_image(self._frame_name, base_infor, sub_infor, current_frame, total_frame,
                                                  fontScale=self.draw_font, merge_axis=self._img_merging_axis)
            if check_value(self.view_image):
                height, width = self.view_image.shape[:2]
                self.create_window(width, height, self.window_name, current_frame, total_frame, self.run_trackbar_frame)
                cv2.imshow(self.window_name, self.view_image)
            else:
                self.create_window(self._view_size[0], self._view_size[1], self.window_name, current_frame, total_frame,
                                   self.run_trackbar_frame)
            return 1
        return 0

    def show_data(self):
        self.view_image = self.get_view_image(self._frame_name, self._file_infors['base_data'],
                                              self._file_infors['sub_data'], self._current_frame,
                                              self._num_total_frames,
                                              fontScale=self.draw_font, merge_axis=self._img_merging_axis)
        if self.view_image is not None:
            cv2.imshow(self.window_name, self.view_image)
    def run_player(self):
        self._current_frame = 0
        self._previous_frame = -1
        self._frame_name = None

        self._check_file_dict.clear()
        self._basic_check_dict.clear()

        self.open_play_data_set()
        Run = True
        self._check_continue = False
        self._check_set_trackbar = True

        Run = self.init_player_window(self._num_total_frames, self._current_frame)

        while Run:

            if self._check_set_trackbar and self.check_file_load():
                cv2.setTrackbarPos('frame', self.window_name, self._current_frame)
            else:
                if self._check_set_trackbar and self.check_file_load():
                    self._frame_name = self.get_frame_data(self._current_frame, self._num_total_frames)

            if self._check_continue:
                cmd = cv2.waitKey(1)
                check_value = self.next_data_command(cmd, self._frame_name)

                if self._current_frame < self._num_total_frames:
                    self.save_check_point(self._check_point_pathname)
                    self.prev_num_frame = self._current_frame
                    self._current_frame += 1
                    self._current_frame = min(self._current_frame, self._num_total_frames - 1)

            else:
                self.show_data()
                cmd = cv2.waitKey(0)
                check_value = self.next_data_command(cmd, self._frame_name)
                self.save_check_point(self._check_point_pathname)

                if check_value == 2:
                    self.save_capture_image(self._frame_name, self._capture_save_path, self.view_image,
                                            self._current_frame,
                                            self._check_mode)
                if check_value == -1:
                    self.save_check_point(self._check_point_pathname)
                    print("exit")
                    break


class Data_Extractor:
    def __init__(self, config, name=None):

        self.file_list = None
        self.file_list_pathname = None
        self.base_path = None
        self.data_path = None
        self.play_data_type = "image"
        self.folder_name = name
        self.check_copy = True
        self.file_infors = None
        self.check_mode = "pos"
        self.save_path = None
        self.save_path_dicts = None
        self.data_merging = False
        self.thread_lock = None
        self.save_frame_gap = None
        self.check_same_folder=False

        type_list = Type_list()
        self._image_type_list = type_list._image_type_list
        self._video_type_list = type_list._video_type_list

        self._check_mode_list = type_list._check_mode_list
        self._section_mode_list = type_list._section_mode_list
        self._file_keys = type_list._file_keys

        self.set_config(config, name)

    def get_base_path(self, base_pathname, play_type):
        if play_type in self._image_type_list:
            return base_pathname
        elif play_type in self._video_type_list:
            return os.path.dirname(base_pathname)

    def get_folder_name(self, name, data_pathname, play_type):
        if check_str_value(name):
            return name
        else:
            if play_type in self._video_type_list:
                basename = os.path.basename(data_pathname)
                return os.path.splitext(basename)[0]
            else:
                _path = data_pathname.replace('\\', '/')
                return _path.split('/')[-1]

    def set_config(self, config, name):

        if check_key_value(config, 'play_data_type'):
            self.play_data_type = config['play_data_type']

        self.data_pathname = config['base_path']
        self.base_path = self.get_base_path(self.data_pathname, self.play_data_type)

        if check_key_value(config, 'check_mode'):
            self.check_mode = config['check_mode']
        self.folder_name = self.get_folder_name(name, self.data_pathname, self.play_data_type)

        base_data_conf = \
            {
                "sub_path": "images",
                "type": "image",
                "prefix_name": None,
                "label_color": None,
                "class_infor": None
            }

        sub_data_conf = {

                "Labelme_BBox": {
                    "sub_path": "bbox",
                    "type": "bbox",
                    "prefix_name": "LidarInput",
                    "label_color": None,
                    "class_infor": None
                }
            }

        if check_key_value(config, 'base_data'):
            base_data_conf = config['base_data']
        if check_key_value(config, 'sub_data'):
            sub_data_conf = config['sub_data']

        self.file_infors = OrderedDict()
        self.file_infors['base_data'] = File_infor(self.base_path, base_data_conf)
        self.file_infors['sub_data'] = OrderedDict()

        for key, _conf in sub_data_conf.items():
            if check_key_value(_conf, 'path'):
                _base_path = _conf['path']
            else:
                _base_path = self.base_path
            self.file_infors['sub_data'][key] = File_infor(_base_path, _conf)

        if check_key_value(config, 'check_copy'):
            self.check_copy = config['check_copy']

        if check_key_value(config, 'data_merging'):
            self.data_merging = config['data_merging']
        if check_key_value(config, 'check_same_folder'):
            self.check_same_folder=config['data_merging']

        self.save_path = os.path.join(self.base_path, self.folder_name)
        self.file_list_pathname = self.get_default_file_list_pathname(self.base_path, self.folder_name,
                                                                      self.file_infors['base_data'], self.check_mode)

        if check_key_value(config, 'save_path'):
            self.save_path = config['save_path']

        if check_key_value(config, 'file_list_pathname'):
            self.file_list_pathname = config['file_list_pathname']

        if check_key_value(config, 'save_frame_gap'):
            self.save_frame_gap = config['save_frame_gap']

    def get_default_file_list_pathname(self, base_path, folder_name, infor, list_mode='section'):

        file_list_pathname = None
        if list_mode in infor.check_list_sub_filename:
            _name = infor.check_list_sub_filename[list_mode]
            file_list_pathname = os.path.join(base_path, folder_name + _name)

        return file_list_pathname

    def open_file_dict_lists(self, pathname, mode='section'):
        out_lists = []
        pathname = pathname.replace('\\', '/')
        if os.path.isfile(pathname):
            file_list = [line.rstrip() for line in open(pathname)]
            for file in file_list:
                s_file = file.split(' ')
                if mode == 'list':
                    out_lists.append(Section_file_infor(0, s_file[0], 0))
                elif mode == 'pos':
                    out_lists.append(Section_file_infor(0, s_file[0], s_file[1]))
        return out_lists

    def get_summery_section_and_types(self, file_list, check_section=False):
        type_list = []
        for file in file_list:
            if file.pos_type not in type_list:
                type_list.append(file.pos_type)
        return type_list

    def check_sub_path(self, sub_path):
        if sub_path == None or sub_path == '':
            return 0
        return 1

    def make_save_folder(self, save_path, add_sub_path, base_sub_path=None, merging=False, same_folder=True):
        _save_path = None
        if merging:
            if base_sub_path is None or base_sub_path == ''or same_folder: #
                _save_path = save_path
            else:
                _save_path = os.path.join(save_path, base_sub_path)

        else:
            if base_sub_path is None or base_sub_path == '' or same_folder:
                _save_path = os.path.join(save_path, add_sub_path)
            else:
                _save_path = os.path.join(save_path, add_sub_path, base_sub_path)

        loader.make_folder(_save_path)
        return _save_path

    def make_folder_dict(self, file_infor, save_path, folder_name, file_list, mode="pos", merging=False, same_folder=True):

        dir_dict = OrderedDict()
        base_infor = file_infor['base_data']
        sub_infor = file_infor['sub_data']


        type_lists = self.get_summery_section_and_types(file_list, check_section=False)
        for _type in type_lists:
            dir_dict[_type] = OrderedDict()

            sub_folder_name = '0_' + folder_name + '_' + str(_type)
            print(sub_folder_name)
            dir_dict[_type]['base_data'] = self.make_save_folder(save_path, sub_folder_name, base_infor.sub_path,
                                                                     merging=merging, same_folder=same_folder)
            print("main save_folder:", _type, dir_dict[_type]['base_data'])
            for key, _infor in sub_infor.items():
               dir_dict[_type][key] = self.make_save_folder(save_path, sub_folder_name, _infor.sub_path,
                                                                 merging=merging, same_folder=same_folder)
               print(" - sub save_folder:",key,  dir_dict[_type][key])
        return dir_dict

    def copy_file_data(self, file_infor, save_path, data, target_prefix=None, check_copy=True):
        file_name = loader.get_target_file_name(data.file_name, target_prefix, file_infor.prefix,
                                       change_ext=file_infor._file_ext)
        src_path_name = os.path.join(file_infor.data_path, file_name)
        save_path_name = os.path.join(save_path, file_name)

        if check_copy:
            shutil.copy(src_path_name, save_path_name)
        else:
            shutil.move(src_path_name, save_path_name)

    def save_data(self, save_path, file_name, data):
        if data is not None:
            save_path_name = os.path.join(save_path, file_name)
            cv2.imwrite(save_path_name, data)
        else:
            print('Fail to save:', file_name)

    def copy_data(self, file_data):

        if file_data.check_data:
            base_infor = self.file_infors['base_data']
            sub_infor = self.file_infors['sub_data']
            target_prefix = base_infor.prefix

            _path_key = file_data.get_section_type(self.check_mode, self._section_mode_list)

            save_path = self.save_paths[_path_key]['base_data']
            self.copy_file_data(base_infor, save_path, file_data, target_prefix=target_prefix,
                                check_copy=self.check_copy)
            for key, _infor in sub_infor.items():
                save_path = self.save_paths[_path_key][key]
                self.copy_file_data(_infor, save_path, file_data, target_prefix=target_prefix,
                                    check_copy=self.check_copy)

    def save_data_list(self, file_list):
        for file in tqdm.tqdm(file_list, desc='copy'):
            idx = fl.get_file_name_index(file.file_name)
            _name, image = self.video_data.get_frame(idx)
            _path_key = file.get_section_type(self.check_mode, self._section_mode_list)
            save_path = self.save_paths[_path_key]['base_data']
            self.save_data(save_path, file.file_name, image)

    def check_video(self, play_type):
        if play_type in self._video_type_list:
            return 1
        return 0

    def run(self):

        file_list = self.open_file_dict_lists(self.file_list_pathname, mode=self.check_mode)
        self.save_paths = self.make_folder_dict(self.file_infors, self.save_path, self.folder_name, file_list,
                                                self.check_mode, merging=self.data_merging)

        if len(file_list) > 0:
            num_cores = multiprocessing.cpu_count()
            pool = multiprocessing.Pool(processes=num_cores)
            list(tqdm.tqdm(pool.imap(self.copy_data, file_list), total=len(file_list)))



def dictionary_shffle(_dict):

    keys=list(_dict.keys())
    random.shuffle(keys)
    out_dict = {key: _dict[key] for key in keys}
    return out_dict

class data_allocator():
    def __init__(self, config):
        self._items = config['items']
        self._out_base_path = config['out_path']
        self.item_confs = OrderedDict()
        self.item_outpaths = OrderedDict()
        for item in self._items:
            self.item_confs[item] = config[item]
            self.item_outpaths[item] = os.path.join(self._out_base_path, item)

        # self._out_task_paths=self.get_task_out_folder(self._items, self._out_basepath, self.item_confs)

    '''
    def get_task_out_folder(self, item_list,out_basepath, configs):
        task_out_patsh=OrderedDict()
        for item in item_list:
            out_path=os.path.join(out_basepath, item)
            file_loader.make_folder(out_path)
            num_data=configs[item]["num_data"]
   '''

    def get_split_data(self, paired_dict, num_data, out_path, task_name=""):
        num_task = int(len(paired_dict) / num_data)
        remain = len(paired_dict) % num_data
        if remain > 0:
            num_task += 1

        in_data = list(paired_dict.keys())
        alloc_data = OrderedDict()
        start_idx = 0
        end_idx = 0
        for cnt in range(num_task):
            _name = task_name + str(cnt)
            alloc_data[_name] = OrderedDict()
            alloc_data[_name]["path"] = os.path.join(out_path, _name)
            alloc_data[_name]["data"] = OrderedDict()
            if remain > 0 and cnt == num_task - 1:
                start_idx = end_idx
                end_idx = end_idx + remain
            else:
                start_idx = end_idx
                end_idx = end_idx + num_data

            file_list = in_data[start_idx:end_idx]
            for file in file_list:
                alloc_data[_name]["data"][file] = paired_dict[file]
            print(" -Slicing:", _name, len(alloc_data[_name]["data"]))
        return alloc_data

    def get_single_data_split(self, data_list, num_data, out_path, task_name=""):
        num_task = int(len(data_list) / num_data)
        remain = len(data_list) % num_data
        if remain > 0:
            num_task += 1

        alloc_data = OrderedDict()
        start_idx = 0
        end_idx = 0
        for cnt in range(num_task):
            _name = task_name + str(cnt)
            alloc_data[_name] = OrderedDict()
            alloc_data[_name]["path"] = os.path.join(out_path, _name)
            alloc_data[_name]["data"] = []
            if remain > 0 and cnt == num_task - 1:
                start_idx = end_idx
                end_idx = end_idx + remain
            else:
                start_idx = end_idx
                end_idx = end_idx + num_data

            file_list = data_list[start_idx:end_idx]
            for file in file_list:
                alloc_data[_name]["data"].append(file)
            print(" -Slicing:", _name, len(alloc_data[_name]["data"]))
        return alloc_data

    def copy_split_data(self, allocated_dict):

        for key, item in allocated_dict.items():
            loader.make_folder(item["path"])
            for file, label in item['data'].items():
                data_name = os.path.basename(file)
                label_name = os.path.basename(label)
                data_pathname = os.path.join(item["path"], data_name)
                label__pathname = os.path.join(item["path"], label_name)
                shutil.copyfile(file, data_pathname)
                shutil.copyfile(label, label__pathname)
    def copy_single_split_data(self, allocated_dict):
        for key, item in allocated_dict.items():
            loader.make_folder(item["path"])
            for file in item['data']:
                data_name = os.path.basename(file)
                data_pathname = os.path.join(item["path"], data_name)
                shutil.copyfile(file, data_pathname)


    def run_task_allocating(self):
        loader.make_folder(self._out_base_path)
        for item in self._items:
            print("Spliting:", item)
            out_path = self.item_outpaths[item]
            data_path = self.item_confs[item]['data_path']
            valid_exts = self.item_confs[item]['valid_exts']
            label_path = self.item_confs[item]['label_path']
            label_ext = self.item_confs[item]['label_ext']
            num_data = self.item_confs[item]['num_data']
            check_shuffle=self.item_confs[item]['shuffle']

            loader.make_folder(out_path)

            paired_list = loader.get_paired_file_list_single_folder(data_path, label_path, valid_exts, label_ext)

            if check_shuffle:
                paired_list=dictionary_shffle(paired_list)


            split_data = self.get_split_data(paired_list, num_data, out_path)
            self.copy_split_data(split_data)
            # print(alloc_data)
            # print("test")


    def run_single_data_task_allocating(self):
        loader.make_folder(self._out_base_path)
        for item in self._items:
            print("Spliting:", item)
            out_path = self.item_outpaths[item]
            data_path = self.item_confs[item]['data_path']
            valid_exts = self.item_confs[item]['valid_exts']
            num_data = self.item_confs[item]['num_data']
            loader.make_folder(out_path)

            data_list = loader.get_files_from_folder(data_path, valid_exts,check_sub_dir=True, check_list=True)
            split_data = self.get_single_data_split(data_list, num_data, out_path)
            self.copy_single_split_data(split_data)


    def run_task_allocating_v2(self):
        loader.make_folder(self._out_base_path)
        for item in self._items:
            print("Spliting:", item)
            out_path = self.item_outpaths[item]
            data_path = self.item_confs[item]['data_path']
            valid_exts = self.item_confs[item]['valid_exts']
            label_path = self.item_confs[item]['label_path']
            label_ext = self.item_confs[item]['label_ext']
            num_data = self.item_confs[item]['num_data']
            loader.make_folder(out_path)

            paired_list = loader.get_paired_file_list_single_folder(data_path, label_path, valid_exts, label_ext)
            split_data = self.get_split_data(paired_list, num_data, out_path)
            self.copy_split_data(split_data)

