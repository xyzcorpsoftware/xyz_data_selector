import os
import time

import numpy as np
import cv2
import json
from common import data_loader as loader
from common.data_structure import *
import json
from collections import OrderedDict
import shutil


def convert_id_to_color(img, color_lists, roi_rects=None):
    if img is not None:
        color_map = np.zeros_like(img)
        if color_lists is not None:
            for i, c in enumerate(color_lists):
                color_map[np.where(img == i)[:2]] = c

        if roi_rects is not None:
            for rect in roi_rects:
                if rect is not None:
                    if rect.color is not None:
                        color_map[rect.y1:rect.y2, rect.x1:rect.x2] = rect.color
        return color_map

    return None


def draw_data_alpha_blend(img, data_list, type='rect', alpha=0.35, thick=3):
    if data_list is not None:
        _image = img.copy()
        if type == 'rect':
            for _rect in data_list:
                x1, y1, x2, y2=_rect.get_draw_roi_rect()
                cv2.rectangle(_image, (x1, y1), (x2, y2), _rect.color, thick)

        _image = cv2.addWeighted(_image, alpha, img, 1 - alpha, 0)

        return _image

    return img

def draw_bbox(image, bbox_lists, base_size=[1920, 1080], roi_rect=None,color_list=None,check_msg=False,thick=1,draw_font=1):
    x_ratio=1
    y_ratio=1
    if roi_rect is not None and base_size is not None:
        x_ratio=roi_rect.width()/base_size[1]
        y_ratio=roi_rect.height()/base_size[0]

    for idx, box in enumerate(bbox_lists):
        if color_list is None:
            if box.color is None:
                _color = (255, 255, 255)
            else:
                _color=box.color
        else:
            if len(color_list)<=box.classID:
                _color=(255,255,255)
            else:
                _color=color_list[box.classID]

        x1, y1, x2, y2=box.get_draw_roi_rect(roi_rect=roi_rect,x_ratio=x_ratio, y_ratio=y_ratio)
        cv2.rectangle(image, (x1, y1), (x2,y2), _color, lineType=cv2.LINE_AA, thickness=thick)

        if check_msg:
            disp_pt = (x1, y1)
            cv2.putText(image, str(box.className), disp_pt, cv2.FONT_HERSHEY_SIMPLEX, draw_font, _color, thick, cv2.LINE_AA)