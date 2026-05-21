from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
import json
import shutil
from collections import OrderedDict
import numpy as np
from common.data_structure import *

def get_sub_folder(path):
    _path = path.replace('\\', '/')
    folder_name = _path.split('/')[-1]
    return folder_name

def make_folder(folder):
    if os.path.exists(folder):
        return -1
    os.makedirs(folder)



def check_key_value(config, key):

    if key in config:
        if config[key] ==None:
            return False
        else:
            return True

    return False

def get_target_file_name(data_name, target_sentence, change_sentence,data_path=None, change_ext=None):
    if check_str_value(target_sentence):
        _file_name=data_name.replace(target_sentence, change_sentence)
    else:
        _file_name=data_name

    if check_str_value(change_ext):
        _file_name = os.path.splitext(_file_name)[0] + change_ext

    if check_str_value(data_path):
        return os.path.join(data_path, _file_name)

    return _file_name


def get_files_from_folder(base_path, valid_exts=["jpg", "gif", "png", "tga", "jpeg", "JPG","bmp"], check_sub_dir=False,
                          check_full_dir=False,check_list=False, except_foders=[]):

    base_path = base_path.replace('\\', '/')
    if check_list:
        file_lists = []
    else:
        file_lists = OrderedDict()
    total_data = 0
    for path, dirs, files in os.walk(base_path):
        dirs.sort()
        file_list = []
        _dir = path.replace('\\', '/')
        upper_path = _dir.split('/')[-1]
        sub_dir = _dir.replace(base_path, '').strip('/')

        if upper_path not in except_foders:
            for filename in sorted(files):
                ext = filename.split('.')[-1]
                if ext in valid_exts:
                    if check_sub_dir:
                        file_list.append(sub_dir + '/' + filename)
                    elif check_full_dir:
                        file_list.append(os.path.join(base_path, sub_dir, filename))
                    else:
                        file_list.append(filename)
            if len(file_list) > 0:
                file_list.sort()
                total_data += len(file_list)
                if check_list:
                    file_lists.extend(file_list)
                else:
                    file_lists[sub_dir] = file_list
                print(" -%s -> Find %d data." % (path, len(file_list)))
                # final_files=self.extract_file_list(file_lists,valid_exts=valid_exts)
    print(" - # Total Data:", total_data)
    return file_lists

def get_couple_file_name(file_name, base_dir=None, sub_path=None, label_ext=".json"):
    base_name = os.path.basename(file_name)
    _name = os.path.splitext(base_name)[0]
    if base_dir is None:
        label_name = '%s%s' % (_name, label_ext)
        return label_name
    if sub_path is None:
        label_name = os.path.join(base_dir, '%s%s' % (_name, label_ext))
        return label_name

    if base_dir == sub_path:
        label_name = '%s%s' % (_name, label_ext)
        return base_name, label_name
    else:
        label_name = '%s/%s%s' % (sub_path, _name, label_ext)
        conv_file_name = '%s/%s' % (sub_path, base_name)
        return conv_file_name, label_name

def get_paired_file_list_single_folder(data_path, label_path, data_exts=["jpg", "gif", "png", "tga", "jpeg", "JPG"],
                                       label_ext='.json', check_path=True, check_print=True):

    file_list = get_files_from_folder(data_path, valid_exts=data_exts,check_list=True)
    couple_list = OrderedDict()

    for file in file_list:
        label_name=get_couple_file_name(file,label_ext=label_ext)
        label_pathname=os.path.join(label_path, label_name)
        label_pathname = label_pathname.replace("\\", '/')
        if os.path.isfile(label_pathname):
            if check_path:
                data_pathname=os.path.join(data_path,file)
                data_pathname = data_pathname.replace("\\", '/')
                couple_list[data_pathname]=label_pathname
            else:
                couple_list[file]=label_name
        else:
            if check_print:
                print(" -", label_path,"-> no matching data")
                print(label_name)

    #print(couple_list)
    print(  " - Matching file: %d"%(len(couple_list)))
    return couple_list

def open_file_list(data_pathname, item_idx=0):
    file_list = [line.rstrip() for line in open(data_pathname)]
    if item_idx:
        files = []
        for file in file_list:
            files.append(file.split(' ')[item_idx])
        return files
    return file_list

def get_color_in_color_dict(color_list, class_id):
    _color=None
    if color_list is not None:
        if class_id >=len(color_list):
            _color=[255,255,255]
        else:
            _color = color_list[class_id]
    return _color


def get_index_file_name(name, pos, num_zero=6, ext=".png"):
    _name = str(pos).zfill(num_zero) + ext
    if check_str_value(name):
        _name = "%s_%s" % (name, _name)
    return _name

def get_file_name_index(file_name):
    _name= os.path.splitext(file_name)[0]
    _index=int(_name.split('_')[-1])
    return _index

def save_checked_pos_file_dict(pathname, check_dict, check_type=True):
    with open(pathname, 'w') as f:
        for _name, value in check_dict._check_names.items():
            if check_type:
                _text = _name + ' ' + str(value['type'])
            else:
                _text= _name

            print(_text, file=f)


def Open_Labelme_Data(pathname, region_type='rectangle', class_dicts=None, color_list=None):
    out_lists = []
    if os.path.isfile(pathname):
        data = json.load(open(pathname, 'r'))
        width = data['imageWidth']
        height = data['imageHeight']
        _color = None
        region_type_list=["polygon", "rectangle", 'polygon']

        if 'shapes' in data:
            for label in data['shapes']:
                if 'shape_type' in label and 'points' in label:
                    _id=0
                    _cls_name=label['label']
                    if class_dicts is not None:
                        if _cls_name in class_dicts:
                            _id=class_dicts[_cls_name]
                            _color=get_color_in_color_dict(color_list,_id)
                            if label['shape_type']==region_type:
                                _rect = label['points']
                                _bbox = BBox(_rect[0][0], _rect[0][1], _rect[1][0], _rect[1][1], classID=_id,
                                                className=_cls_name, color=_color)
                                out_lists.append(_bbox)
                    else:
                        if label['shape_type'] == region_type:
                            _rect = label['points']
                            _bbox = BBox(_rect[0][0], _rect[0][1], _rect[1][0], _rect[1][1], classID=-1,
                                         className=_cls_name,)
                            out_lists.append(_bbox)

    return out_lists

def Open_Label_Data( data_type, data_pathname, class_infor, label_color):
    data=None

    if data_type =='Labelme_BBox':
        data=Open_Labelme_Data(data_pathname, region_type='rectangle', class_dicts=class_infor, color_list=label_color)
    return data
