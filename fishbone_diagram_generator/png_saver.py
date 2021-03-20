"""
Module for exporting PNG files
"""
import copy
import cv2
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap
import numpy as np
import math
import fishbone_diagram_generator.const as const


class PNGSaver():
    """ Class for PNG file export """

    def __init__(self, filepath, painter):
        self.filepath = filepath
        self.fishbone = copy.deepcopy(painter.fishbone)
        self.offset_fishbone()
        self.to_integer()
        self.img = None

    def to_integer(self):
        self.fishbone.main_bone[0] = self.fishbone.main_bone[0].to_integer()
        self.fishbone.main_bone[1] = self.fishbone.main_bone[1].to_integer()

        for sub_bone in self.fishbone.sub_bones:
            sub_bone.to_integer()

    def offset_fishbone(self):
        min_x = 0
        min_y = 0
        max_x = 0
        max_y = 0

        for sub_bone in self.fishbone.sub_bones:
            if min_x > sub_bone.rect.pos[0]:
                min_x = sub_bone.rect.pos[0]
            if min_y > sub_bone.rect.pos[1]:
                min_y = sub_bone.rect.pos[1]

        if self.fishbone.direction == 'left':
            x = self.fishbone.main_bone[1].x - 400 - 50
            if min_x > x:
                min_x = x

        dx = -min_x + const.HORIZONTAL_MARGIN
        dy = -min_y + const.VERTICAL_MARGIN

        self.fishbone.main_bone[0] = self.fishbone.main_bone[0].offset(dx, dy)
        self.fishbone.main_bone[1] = self.fishbone.main_bone[1].offset(dx, dy)

        for sub_bone in self.fishbone.sub_bones:
            sub_bone.offset(dx, dy)

        for sub_bone in self.fishbone.sub_bones:
            x = sub_bone.rect.pos[0] + sub_bone.rect.size[0]
            y = sub_bone.rect.pos[1] + sub_bone.rect.size[1]
            if max_x < x:
                max_x = x
            if max_y < y:
                max_y = y

        max_y = max_y + const.VERTICAL_MARGIN * 2

        if self.fishbone.direction == 'left':
            x = self.fishbone.main_bone[0].x + const.HORIZONTAL_MARGIN
            if max_x < x:
                max_x = x
        else:
            x = self.fishbone.main_bone[1].x + 400 + 50
            if max_x < x:
                max_x = x

        self.size = (int(max_x), int(max_y))

    def save(self):
        self.img = np.full(
            (self.size[1], self.size[0], 3), 255, dtype=np.uint8)

        bone_color = (int(const.MAIN_SUB_BONE_COLOR[0] * 255), int(
            const.MAIN_SUB_BONE_COLOR[1] * 255), int(const.MAIN_SUB_BONE_COLOR[2] * 255))

        main_bone_text_color = (int(const.MAIN_BONE_TEXT_COLOR[0] * 255), int(
            const.MAIN_BONE_TEXT_COLOR[1] * 255), int(const.MAIN_BONE_TEXT_COLOR[2] * 255))

        cv2.line(self.img, (self.fishbone.main_bone[0].x, self.fishbone.main_bone[0].y), (
            self.fishbone.main_bone[1].x + 2, self.fishbone.main_bone[1].y), (bone_color[2], bone_color[1], bone_color[0]), 30, lineType=cv2.LINE_AA)

        if self.fishbone.direction == 'left':
            pts = np.array([[self.fishbone.main_bone[1].x, self.fishbone.main_bone[1].y - 35],
                            [self.fishbone.main_bone[1].x - 45,
                             self.fishbone.main_bone[1].y],
                            [self.fishbone.main_bone[1].x, self.fishbone.main_bone[1].y + 35]], np.int32)
        else:
            pts = np.array([[self.fishbone.main_bone[1].x, self.fishbone.main_bone[1].y - 35],
                            [self.fishbone.main_bone[1].x + 45,
                             self.fishbone.main_bone[1].y],
                            [self.fishbone.main_bone[1].x, self.fishbone.main_bone[1].y + 35]], np.int32)

        pts = pts.reshape((-1, 1, 2))
        cv2.fillPoly(self.img, [pts], (bone_color[2],
                                       bone_color[1], bone_color[0]), lineType=cv2.LINE_AA)

        if self.fishbone.direction == 'left':
            self.add_text_area(self.fishbone.text, self.fishbone.main_bone[1].x - 50 - 400,
                               self.fishbone.main_bone[1].y - 100, 400, 200, 'right', 'middle', 20, (main_bone_text_color[2], main_bone_text_color[1], main_bone_text_color[0]))
        else:
            self.add_text_area(self.fishbone.text, self.fishbone.main_bone[1].x + 50,
                               self.fishbone.main_bone[1].y - 100, 400, 200, 'left', 'middle', 20, (main_bone_text_color[2], main_bone_text_color[1], main_bone_text_color[0]))

        index = 0
        side = ''

        for sub_bone in self.fishbone.sub_bones:

            if index % 2 == 0:
                side = 'up'
                dx = int(math.sin(math.radians(const.DEG)) * 15)
                dy = int(math.cos(math.radians(const.DEG)) * 15)

                if self.fishbone.direction == 'left':
                    dx = -dx

                self.add_text_area(
                    sub_bone.text,
                    sub_bone.bone[0].x - sub_bone.get_width() / 2,
                    sub_bone.bone[0].y - const.VERTICAL_MARGIN - 15, sub_bone.get_width(), const.VERTICAL_MARGIN, 'center', 'bottom', 20, (bone_color[2], bone_color[1], bone_color[0]))
            else:
                side = 'down'
                dx = int(math.sin(math.radians(const.DEG)) * 15)
                dy = int(-math.cos(math.radians(const.DEG)) * 15)

                if self.fishbone.direction == 'left':
                    dx = -dx

                self.add_text_area(
                    sub_bone.text,
                    sub_bone.bone[0].x - sub_bone.get_width() / 2,
                    sub_bone.bone[0].y + 15, sub_bone.get_width(), const.VERTICAL_MARGIN, 'center', 'top', 20, (bone_color[2], bone_color[1], bone_color[0]))

            cv2.line(self.img, (sub_bone.bone[0].x, sub_bone.bone[0].y), (
                sub_bone.bone[1].x - dx, sub_bone.bone[1].y - dy),
                (bone_color[2], bone_color[1], bone_color[0]),
                10, lineType=cv2.LINE_AA
            )

            pts = np.array([[sub_bone.arrow[0].x, sub_bone.arrow[0].y],
                            [sub_bone.arrow[1].x,
                             sub_bone.arrow[1].y],
                            [sub_bone.arrow[2].x,
                             sub_bone.arrow[2].y]], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.fillPoly(self.img, [pts], (bone_color[2],
                                           bone_color[1], bone_color[0]), lineType=cv2.LINE_AA)

            index = index + 1

            for bone in sub_bone.child_bones:
                self.add_bone_line(bone)
                self.add_bone_text(bone, side)

        cv2.imwrite(self.filepath, self.img)

    def add_bone_text(self, bone, side):
        if bone.direction == 'vertical':
            if side == 'up':
                self.add_text_area(bone.text, bone.bone[0].x - bone.get_width() / 2, bone.bone[0].y - const.VERTICAL_MARGIN, bone.get_width(
                ), const.VERTICAL_MARGIN, 'center', 'bottom', 10, (0, 0, 0))
            else:
                self.add_text_area(bone.text, bone.bone[0].x - bone.get_width() / 2, bone.bone[0].y + 5, bone.get_width(
                ), const.VERTICAL_MARGIN, 'center', 'top', 10, (0, 0, 0))
        else:

            if side == 'up':
                if self.fishbone.direction == 'left':
                    self.add_text_area(bone.text, bone.bone[0].x, bone.bone[0].y + 5, bone.get_width(
                    ), const.VERTICAL_MARGIN, 'right', 'top', 10, (0, 0, 0))
                else:
                    self.add_text_area(bone.text, bone.bone[0].x, bone.bone[0].y + 5, bone.get_width(
                    ), const.VERTICAL_MARGIN, 'left', 'top', 10, (0, 0, 0))
            else:
                if self.fishbone.direction == 'left':
                    self.add_text_area(bone.text, bone.bone[0].x, bone.bone[0].y - const.VERTICAL_MARGIN - 5, bone.get_width(
                    ), const.VERTICAL_MARGIN, 'right', 'bottom', 10, (0, 0, 0))
                else:
                    self.add_text_area(bone.text, bone.bone[0].x, bone.bone[0].y - const.VERTICAL_MARGIN - 5, bone.get_width(
                    ), const.VERTICAL_MARGIN, 'left', 'bottom', 10, (0, 0, 0))

        for child_bone in bone.child_bones:
            self.add_bone_text(child_bone, side)

    def add_bone_line(self, bone):
        cv2.line(self.img,
                 (bone.bone[0].x, bone.bone[0].y),
                 (bone.bone[1].x, bone.bone[1].y),
                 (0, 0, 0),
                 1, lineType=cv2.LINE_AA)

        pts = np.array([[bone.arrow[0].x, bone.arrow[0].y],
                        [bone.arrow[1].x, bone.arrow[1].y],
                        [bone.arrow[2].x, bone.arrow[2].y]], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.fillPoly(self.img, [pts], (0, 0, 0), lineType=cv2.LINE_AA)

        for child_bone in bone.child_bones:
            self.add_bone_line(child_bone)

    def add_text_area(self, text, x, y, width, height, halign, valign, size, color):
        text_wrap = textwrap.fill(text, int(width / size))

        imgPIL = Image.fromarray(self.img)
        draw = ImageDraw.Draw(imgPIL)

        if os.path.exists('fishbone_diagram_generator/fonts/ipaexg.ttf'):
            fontPIL = ImageFont.truetype(
                font='fishbone_diagram_generator/fonts/ipaexg.ttf', size=size)
        else:
            fontPIL = ImageFont.truetype(font='Roboto-Regular.ttf', size=size)

        bbox = draw.multiline_textbbox((0, 0), text_wrap, font=fontPIL)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        if halign == 'center':
            if valign == 'middle':
                dx = width / 2 - w / 2
                dy = height / 2 - h / 2

                xy = (int(x + dx), int(y + dy))
            elif valign == 'top':
                dx = width / 2 - w / 2

                xy = (int(x + dx), y)
            else:
                dx = width / 2 - w / 2
                dy = height - h

                xy = (int(x + dx), int(y + dy))
        elif halign == 'left':
            if valign == 'middle':
                dy = height / 2 - h / 2

                xy = (x, int(y + dy))
            elif valign == 'top':
                xy = (x, y)
            else:
                dy = height - h

                xy = (x, int(y + dy))
        else:
            if valign == 'middle':
                dx = width - w
                dy = height / 2 - h / 2

                xy = (int(x + dx), int(y + dy))
            elif valign == 'top':
                dx = width - w

                xy = (int(x + dx), y)
            else:
                dx = width - w
                dy = height - h

                xy = (int(x + dx), int(y + dy))

        draw.text(xy=xy, text=text_wrap,
                  fill=color, font=fontPIL)

        self.img = np.array(imgPIL, dtype=np.uint8)
