"""
Module for exporting SVG files
"""
import svgwrite
import math
import copy
import fishbone_diagram_generator.const as const


class ForeignObject(svgwrite.base.BaseElement, svgwrite.mixins.Transform, svgwrite.container.Presentation):
    """ ForeignObject compatible class """
    elementname = 'foreignObject'

    def __init__(self, obj, **extra):
        super().__init__(**extra)
        self.obj = obj

    def get_xml(self):
        xml = super().get_xml()
        xml.append(svgwrite.etree.etree.fromstring(self.obj))
        return xml


svgwrite.elementfactory.factoryelements['foreignObject'] = ForeignObject


class SVGSaver():
    """ Class for SVG file export """

    def __init__(self, filepath, painter):
        self.filepath = filepath
        self.fishbone = copy.deepcopy(painter.fishbone)
        self.offset_fishbone()

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

        self.size = (max_x, max_y)

    def save(self):
        dwg = svgwrite.Drawing(self.filepath, size=self.size)

        bone_color = (int(const.MAIN_SUB_BONE_COLOR[0] * 255), int(
            const.MAIN_SUB_BONE_COLOR[1] * 255), int(const.MAIN_SUB_BONE_COLOR[2] * 255))

        main_bone_text_color = (int(const.MAIN_BONE_TEXT_COLOR[0] * 255), int(
            const.MAIN_BONE_TEXT_COLOR[1] * 255), int(const.MAIN_BONE_TEXT_COLOR[2] * 255))

        dwg.add(dwg.line((self.fishbone.main_bone[0].x, self.fishbone.main_bone[0].y), (
            self.fishbone.main_bone[1].x + 2, self.fishbone.main_bone[1].y),
            stroke=svgwrite.rgb(bone_color[0], bone_color[1], bone_color[2]),
            stroke_width='30'
        ))
        if self.fishbone.direction == 'left':
            dwg.add(dwg.polygon(
                points=[(self.fishbone.main_bone[1].x + 3, self.fishbone.main_bone[1].y - 35),
                        (self.fishbone.main_bone[1].x - 45 + 3,
                         self.fishbone.main_bone[1].y),
                        (self.fishbone.main_bone[1].x + 3, self.fishbone.main_bone[1].y + 35)],
                fill=svgwrite.rgb(bone_color[0], bone_color[1], bone_color[2]), stroke='none')
            )
        else:
            dwg.add(dwg.polygon(
                points=[(self.fishbone.main_bone[1].x, self.fishbone.main_bone[1].y - 35),
                        (self.fishbone.main_bone[1].x + 45,
                         self.fishbone.main_bone[1].y),
                        (self.fishbone.main_bone[1].x, self.fishbone.main_bone[1].y + 35)],
                fill=svgwrite.rgb(bone_color[0], bone_color[1], bone_color[2]), stroke='none')
            )
        dwg.add(dwg.style(
            ' .main_bone_style {font-size: 25px;color: RGB(' + str(main_bone_text_color[0]) + ',' + str(
                main_bone_text_color[1]) + ',' + str(main_bone_text_color[2]) + ')} '
            ' .sub_bone_style {font-size: 25px; line-height: 30px; color: RGB(' + str(
                bone_color[0]) + ',' + str(bone_color[1]) + ',' + str(bone_color[2]) + ')} '
            ' .sub_bone_text_style {font-size: 9px; line-height: 11px}'))

        if self.fishbone.direction == 'left':
            self.add_text_area(dwg, self.fishbone.text, self.fishbone.main_bone[1].x - 50 - 400,
                               self.fishbone.main_bone[1].y - 100, 400, 200, 'right', 'middle', 'main_bone_style')
        else:
            self.add_text_area(dwg, self.fishbone.text, self.fishbone.main_bone[1].x + 50,
                               self.fishbone.main_bone[1].y - 100, 400, 200, 'left', 'middle', 'main_bone_style')

        index = 0
        side = ''

        for sub_bone in self.fishbone.sub_bones:

            if index % 2 == 0:
                side = 'up'
                dx = math.sin(math.radians(const.DEG)) * 10
                dy = math.cos(math.radians(const.DEG)) * 10

                if self.fishbone.direction == 'left':
                    dx = -dx

                self.add_text_area(
                    dwg, sub_bone.text,
                    sub_bone.bone[0].x - sub_bone.get_width() / 2,
                    sub_bone.bone[0].y - const.VERTICAL_MARGIN, sub_bone.get_width(), const.VERTICAL_MARGIN, 'center', 'bottom', 'sub_bone_style')
            else:
                side = 'down'
                dx = math.sin(math.radians(const.DEG)) * 10
                dy = -math.cos(math.radians(const.DEG)) * 10

                if self.fishbone.direction == 'left':
                    dx = -dx

                self.add_text_area(
                    dwg, sub_bone.text,
                    sub_bone.bone[0].x - sub_bone.get_width() / 2,
                    sub_bone.bone[0].y, sub_bone.get_width(), const.VERTICAL_MARGIN, 'center', 'top', 'sub_bone_style')

            dwg.add(dwg.line((sub_bone.bone[0].x, sub_bone.bone[0].y), (
                    sub_bone.bone[1].x - dx, sub_bone.bone[1].y - dy),
                stroke=svgwrite.rgb(
                    bone_color[0], bone_color[1], bone_color[2]),
                stroke_width='10'
            ))
            dwg.add(dwg.polygon(
                points=[(sub_bone.arrow[0].x, sub_bone.arrow[0].y),
                        (sub_bone.arrow[1].x,
                         sub_bone.arrow[1].y),
                        (sub_bone.arrow[2].x,
                         sub_bone.arrow[2].y)],
                fill=svgwrite.rgb(bone_color[0], bone_color[1], bone_color[2]), stroke='none')
            )
            index = index + 1

            for bone in sub_bone.child_bones:
                self.add_bone_line(bone, dwg)
                self.add_bone_text(bone, dwg, side)

        dwg.save()

    def add_bone_line(self, bone, dwg):
        dwg.add(dwg.line(
            (bone.bone[0].x, bone.bone[0].y),
            (bone.bone[1].x, bone.bone[1].y),
            stroke='black',
            stroke_width='1'
        ))
        dwg.add(dwg.polygon(
                points=[(bone.arrow[0].x, bone.arrow[0].y),
                        (bone.arrow[1].x, bone.arrow[1].y),
                        (bone.arrow[2].x, bone.arrow[2].y)],
                fill='black', stroke='none'))

        for child_bone in bone.child_bones:
            self.add_bone_line(child_bone, dwg)

    def add_bone_text(self, bone, dwg, side):
        if bone.direction == 'vertical':
            if side == 'up':
                self.add_text_area(dwg, bone.text, bone.bone[0].x - bone.get_width() / 2, bone.bone[0].y - const.VERTICAL_MARGIN + 5, bone.get_width(
                ), const.VERTICAL_MARGIN, 'center', 'bottom', 'sub_bone_text_style')
            else:
                self.add_text_area(dwg, bone.text, bone.bone[0].x - bone.get_width() / 2, bone.bone[0].y + 10, bone.get_width(
                ), const.VERTICAL_MARGIN, 'center', 'top', 'sub_bone_text_style')
        else:
            if side == 'up':
                if self.fishbone.direction == 'left':
                    self.add_text_area(dwg, bone.text, bone.bone[0].x, bone.bone[0].y + 5, bone.get_width(
                    ), const.VERTICAL_MARGIN, 'right', 'top', 'sub_bone_text_style')
                else:
                    self.add_text_area(dwg, bone.text, bone.bone[0].x, bone.bone[0].y + 5, bone.get_width(
                    ), const.VERTICAL_MARGIN, 'left', 'top', 'sub_bone_text_style')
            else:
                if self.fishbone.direction == 'left':
                    self.add_text_area(dwg, bone.text, bone.bone[0].x, bone.bone[0].y - const.VERTICAL_MARGIN, bone.get_width(
                    ), const.VERTICAL_MARGIN, 'right', 'bottom', 'sub_bone_text_style')
                else:
                    self.add_text_area(dwg, bone.text, bone.bone[0].x, bone.bone[0].y - const.VERTICAL_MARGIN, bone.get_width(
                    ), const.VERTICAL_MARGIN, 'left', 'bottom', 'sub_bone_text_style')

        for child_bone in bone.child_bones:
            self.add_bone_text(child_bone, dwg, side)

    def add_text_area(self, dwg, text, x, y, w, h, halign, valign, style):
        dwg.add(
            ForeignObject(
                x=x,
                y=y,
                width=w,
                height=h,
                obj='<div xmlns="http://www.w3.org/1999/xhtml"><table width="' + str(w) + '" height="' + str(h) + '"><tr><td align="' + halign + '" valign="' + valign + ' " class="' + style + '">' + text + '</td></tr></table></div>'))
