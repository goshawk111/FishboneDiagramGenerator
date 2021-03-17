"""
Diagram drawing module
"""
import fishbone_diagram_generator.const as const
from fishbone_diagram_generator.fishbone_generator import FishBoneGenerator
from fishbone_diagram_generator.fishbone import Pos
from kivy.uix.label import Label
from kivy.graphics import Color
from kivy.graphics import Triangle
from kivy.graphics import Line


class DiagramPainter():
    """ Diagram drawing class """
    def __init__(self, widget, xml_loader):
        self.widget = widget
        self.xml_loader = xml_loader
        self.fishbone = FishBoneGenerator(xml_loader)
        self.main_bone = None
        self.offset_x = 0
        self.offset_y = 0
        self.sub_bone_lines = []
        self.sub_bone_triangle = []
        self.main_bone_arrow = None
        self.sub_bone_text = []

    def get_pos(self, x, y):
        return Pos(x, self.widget.size[1] - y - 40 - 16)

    def redraw(self, dx, dy):
        if self.fishbone.is_create is True:
            self.offset_x = self.offset_x + dx
            self.offset_y = self.offset_y + dy

            index = 0
            for sub_bone in self.fishbone.sub_bones:
                self.redraw_sub_bones(
                    index, sub_bone, self.offset_x, self.offset_y)
                index = index + 1

            self.widget.remove_widget(self.main_bone_text)
            self.widget.canvas.remove(self.main_bone)
            self.widget.canvas.remove(self.main_bone_arrow)
            self.draw_main_bone(self.fishbone.main_bone,
                                self.offset_x, self.offset_y)
            self.move_sub_bone_string(self.offset_x, self.offset_y)

    def draw(self):
        self.fishbone.create()

        index = 0
        for sub_bone in self.fishbone.sub_bones:
            self.sub_bone_lines.append([])
            self.sub_bone_triangle.append([])
            self.draw_sub_bones(index, sub_bone, 0, 0)
            self.draw_sub_bone_string(index, sub_bone)
            index = index + 1

        self.draw_main_bone(self.fishbone.main_bone, 0, 0)

    def redraw_sub_bones(self, index, bone, dx, dy):
        if len(self.sub_bone_lines[index]) != 0:
            for line in self.sub_bone_lines[index]:
                self.widget.canvas.remove(line)
            self.sub_bone_lines[index].clear()

        if len(self.sub_bone_triangle[index]) != 0:
            for triangle in self.sub_bone_triangle[index]:
                self.widget.canvas.remove(triangle)
            self.sub_bone_triangle[index].clear()

        self.draw_sub_bones(index, bone, dx, dy)

    def draw_sub_bones(self, index, bone, dx, dy):

        with self.widget.canvas:

            if bone.level == 1:
                width = 3
                Color(
                    const.MAIN_SUB_BONE_COLOR[0], const.MAIN_SUB_BONE_COLOR[1], const.MAIN_SUB_BONE_COLOR[2])
            else:
                width = 1
                Color(0, 0, 0)

            p1 = self.get_pos(
                bone.bone[0].x + dx, bone.bone[0].y + dy)
            p2 = self.get_pos(
                bone.bone[1].x + dx, bone.bone[1].y + dy)

            self.sub_bone_lines[index].append(Line(points=[p1.x, p1.y,
                                                           p2.x, p2.y], width=width))

            ap1 = self.get_pos(bone.arrow[0].x + dx, bone.arrow[0].y + dy)
            ap2 = self.get_pos(bone.arrow[1].x + dx, bone.arrow[1].y + dy)
            ap3 = self.get_pos(bone.arrow[2].x + dx, bone.arrow[2].y + dy)

            self.sub_bone_triangle[index].append(
                Triangle(points=[ap1.x, ap1.y, ap2.x, ap2.y, ap3.x, ap3.y]))

        for child in bone.child_bones:
            self.draw_sub_bones(index, child, dx, dy)

    def move_sub_bone_string(self, dx, dy):
        for (label, pos) in self.sub_bone_text:
            label.pos = self.get_pos(pos.x + dx, pos.y + dy).get_tuple()

    def draw_sub_bone_string(self, index, bone):

        if bone.level == 1:
            size = 20
            font_color = const.MAIN_SUB_BONE_COLOR
            margin = 3

        else:
            size = 10
            font_color = (0, 0, 0)
            margin = 0
        if index % 2 == 0:
            # Upper side
            if bone.direction == 'vertical':
                halign = 'center'
                valign = 'bottom'
                label_pos = Pos(
                    bone.bone[0].x - bone.get_width() / 2, bone.bone[0].y - 4 - margin)
            else:
                halign = 'left'
                valign = 'top'
                label_pos = Pos(
                    bone.bone[0].x, bone.bone[0].y + const.VERTICAL_MARGIN + 3)
        else:
            # Lower side
            if bone.direction == 'vertical':
                halign = 'center'
                valign = 'top'
                label_pos = Pos(
                    bone.bone[0].x - bone.get_width() / 2, bone.bone[0].y + const.VERTICAL_MARGIN + 4 + margin)
            else:
                halign = 'left'
                valign = 'bottom'
                label_pos = Pos(
                    bone.bone[0].x, bone.bone[0].y - 3)

        self.sub_bone_text.append((
            Label(text=bone.text, font_size=size, color=font_color, pos=self.get_pos(
                label_pos.x, label_pos.y).get_tuple(), halign=halign, valign=valign,
                width=bone.get_width(), height=const.VERTICAL_MARGIN, text_size=(bone.get_width(), const.VERTICAL_MARGIN)), label_pos)
        )
        self.widget.add_widget(self.sub_bone_text[-1][0])

        for child in bone.child_bones:
            self.draw_sub_bone_string(index, child)

    def draw_main_bone(self, bone, dx, dy):
        self.main_bone_text = Label(text=self.xml_loader.get_effect(
        ), font_size=20, color=(.46, .13, .16), pos=self.get_pos(bone[1].x + dx + 60, bone[1].y + 50 + dy).get_tuple(), width=200, text_size=(200, None), halign='left', valign='top')

        self.widget.add_widget(self.main_bone_text)

        with self.widget.canvas:
            Color(
                const.MAIN_SUB_BONE_COLOR[0], const.MAIN_SUB_BONE_COLOR[1], const.MAIN_SUB_BONE_COLOR[2])

            p1 = self.get_pos(bone[0].x + dx, bone[0].y + dy)
            p2 = self.get_pos(bone[1].x + dx, bone[1].y + dy)

            self.main_bone = Line(
                points=[p1.x, p1.y, p2.x, p2.y], width=const.MAIN_BONE_WIDTH)

            ap1 = self.get_pos(bone[1].x + 50 + dx, bone[1].y + dy)
            ap2 = self.get_pos(bone[1].x + 50 - 50 + dx, bone[1].y + 20 + dy)
            ap3 = self.get_pos(bone[1].x + 50 - 50 + dx, bone[1].y - 20 + dy)

            self.main_bone_arrow = Triangle(
                points=[ap1.x, ap1.y, ap2.x, ap2.y, ap3.x, ap3.y])
