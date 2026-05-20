from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json
import shutil
from collections import OrderedDict
import numpy as np


def check_key_value(config, key):
    if key in config:
        if config[key] ==None:
            return False
        else:
            return True

    return False


def check_str_value(value):
    if value is not None:
        return 1
    return 0
def check_value(value):

    if value is not None:
        return 1
    return 0


class Check_Name_Dict:
    def __init__(self):
        #key:파일이름, 'value':속성
        self._check_names=OrderedDict()

    def clear(self):
        self._check_names.clear()

    def add(self, name, pos, _type=0):
        self._check_names[name] = OrderedDict()
        self._check_names[name]['pos']=pos
        self._check_names[name]['type']=_type

    def add_modify_del_by_name(self, _name, pos, _type=0,check_del=False):
        if _name in self._check_names:
            if self._check_names[_name]['type'] != _type:
                self._check_names[_name]['type']= _type
            else:
                if check_del:
                    self._check_names.pop(_name)
        else:
            self.add(_name, pos, _type)

    def del_by_name(self, _name):
        if _name in self._check_names:
            self._check_names.pop(_name)

    def check_name(self, _name):
        if _name in self._check_names:
            return 1
        else:
            return 0
    def get_pos_type(self, _name):
        if _name in self._check_names:
            return self._check_names[_name]['pos'], self._check_names[_name]['type']
        else:
            return -1, -1

    def get_pos(self, _name):
        if _name in self._check_names:
            return self._check_names[_name]['pos']
        else:
            return -1
    def get_type(self, _name):
        if _name in self._check_names:
            return self._check_names[_name]['type']
        else:
            return -1
    def set_color_bar_image(self, img, total_frame, width, color_lists):
        for key, value in self._check_names.items():
            img_pos = int(value['pos'] / total_frame * width)
            img[:, img_pos] = color_lists[value['type']]
        return img


class Section_file_infor:
    def __init__(self, section, file_name, pos_type, check_data=1):
        self.section=section
        self.file_name=file_name
        self.pos_type=pos_type
        self.check_data=check_data

    def get_section_type(self, mode="section", section_list=["section", "excepted_section"]):
        if mode in section_list:
            return self.section
        else:
            return self.pos_type


class Point(object):
    def __init__(self, x1, y1, id=-1, name=None):
        self.x1 = x1
        self.y1 = y1
        self.id = id
        self.name = None


class Rect(object):
    def __init__(self, x1, y1, x2, y2, className=None, color=None, check_sort=True):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.className = className
        if check_sort:
            self.sortCoords()

        self.color = color

    def width(self):
        return self.x2 - self.x1

    def height(self):
        return self.y2 - self.y1

    def get_draw_roi_rect(self, roi_rect=None, x_ratio=1, y_ratio=1):
        if roi_rect is None:
            return int(self.x1 * x_ratio), int(self.y1 * y_ratio), int(self.x2 * x_ratio), int(self.y2 * y_ratio)
        else:
            x1 = (int)(min(self.x1 * x_ratio + roi_rect.x1, roi_rect.x2 - 1))
            y1 = (int)(min(self.y1 * y_ratio + roi_rect.y1, roi_rect.y2 - 1))
            x2 = (int)(min(self.x2 * x_ratio + roi_rect.x1, roi_rect.x2 - 1))
            y2 = (int)(min(self.y2 * y_ratio + roi_rect.y1, roi_rect.y2) - 1)
            return x1, y1, x2, y2

    def sortCoords(self):
        if (self.x1 > self.x2):
            self.x1, self.x2 = self.x2, self.x1
        if (self.y1 > self.y2):
            self.y1, self.y2 = self.y2, self.y1

    def check_out_range(self, width, height):
        interX, interY = self.intersection(None, img_width=width, img_height=height)
        if interX < 0.01:
            return 0
        if interY < 0.01:
            return 0
        return 1

    def intersection(self, other, img_width=None, img_height=None):
        if other is not None:
            other.sortCoords()
            x1 = other.x1
            x2 = other.x2
            y1 = other.y1
            y2 = other.y2
        else:
            if img_width is None or img_height is None:
                return (0, 0)
            x1 = 0
            x2 = img_width
            y1 = 0
            y2 = img_height

        if (self.x1 >= x2):
            return (0, 0)
        if (self.x2 <= x1):
            return (0, 0)
        if (self.y1 >= y2):
            return (0, 0)
        if (self.y2 <= y1):
            return (0, 0)

        l = max(self.x1, x1)
        t = max(self.y1, y1)
        r = min(self.x2, x2)
        b = min(self.y2, y2)
        return (r - l, b - t)

    def area(self):
        return (self.x2 - self.x1) * (self.y2 - self.y1)

    def iou(self, other):
        interX, interY = self.intersection(other)
        if interX < 0.01:
            return 0
        if interY < 0.01:
            return 0
        area1 = self.area()
        area2 = other.area()
        inter = interX * interY
        iou = float(inter) / (area1 + area2 - inter)
        return iou


class BBox(Rect):
    def __init__(self, x1, y1, x2, y2, classID=-1, className=None, score=-1, color=None):
        super(BBox, self).__init__(x1, y1, x2, y2, className, color)
        self.classID = classID
        self.score = score


class A2Z_Lidar_2D_Box:
    def __init__(self, x1, y1, x2, y2, x3, y3, x4, y4, classID=-1, className=None, color=None):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3
        self.x4 = x4
        self.y4 = y4


class Obj_Class():
    def __init__(self, cls_name, id=-1, cls_type=None, score=-1, roi=None, color=None):
        self.cls_name = cls_name
        self.classID = id
        self.cls_type = cls_type
        self.color = color
        self.score = score
        self.roi = roi

