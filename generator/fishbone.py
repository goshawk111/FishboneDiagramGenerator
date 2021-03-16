"""
Fishbone definition module
"""
import math
import util.const as const
import sys
from kivy.graphics import Color
from kivy.graphics import Line

sys.path.append('../util')


class Rect():
    """ Rectangle definition class """
    def __init__(self, x, y, w, h):
        self.pos = [x, y]
        self.size = [w, h]

    def get_str(self):
        return '(x,y) = (' + str(self.pos[0]) + ',' + str(self.pos[1]) + ') (w,h) = (' + str(self.size[0]) + ',' + str(self.size[1]) + ')'


class Pos():
    """ Position definition class """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_integer(self):
        return Pos(int(self.x), int(self.y))

    def get_str(self):
        return '(' + str(self.x) + ',' + str(self.y) + ')'

    def get_tuple(self):
        return (self.x, self.y)

    def offset(self, dx, dy):
        return Pos(self.x + dx, self.y + dy)

    def rotate(self, center, deg):
        offset_pos = self.offset(-center.x, -center.y)

        rot_pos = Pos(
            math.cos(math.radians(deg)) * offset_pos.x - math.sin(math.radians(deg)) * offset_pos.y,
            math.sin(math.radians(deg)) * offset_pos.x + math.cos(math.radians(deg)) * offset_pos.y)

        return rot_pos.offset(center.x, center.y)


class FishBone():
    """ FishBone definition class """
    def __init__(self, parent):
        if parent is None:
            self.level = 1
            self.direction = 'vertical'

        else:
            self.level = parent.level + 1
            if parent.direction == 'vertical':
                self.direction = 'horizontal'
            else:
                self.direction = 'vertical'

        self.bone = [Pos(0, 0), Pos(0, 0)]
        self.text = ''

        self.parent = parent
        self.child_bones = []

        self.rect = Rect(0, 0, 0, 0)
        self.arrow = [Pos(0, 0), Pos(0, 0), Pos(0, 0)]

    def calc_arrow(self):

        if self.direction == 'vertical':
            if self.level == 1:
                w = 10
            else:
                w = 5
            self.arrow[0] = Pos(self.bone[1].x, self.bone[1].y)
            self.arrow[1] = Pos(self.bone[1].x - w, self.bone[1].y - w * 2)
            self.arrow[2] = Pos(self.bone[1].x + w, self.bone[1].y - w * 2)
            deg = -const.DEG
            self.arrow[1] = self.arrow[1].rotate(self.arrow[0], deg)
            self.arrow[2] = self.arrow[2].rotate(self.arrow[0], deg)
        else:
            self.arrow[0] = Pos(self.bone[1].x, self.bone[1].y)
            self.arrow[1] = Pos(self.bone[1].x - 10, self.bone[1].y + 5)
            self.arrow[2] = Pos(self.bone[1].x - 10, self.bone[1].y - 5)

    def print_info(self):
        print('level:', self.level, 'direction:', self.direction,
              'bone:', self.bone[0].get_str() + ',' + self.bone[1].get_str(), 'text:', self.text)

    def to_integer(self):
        self.bone[0] = self.bone[0].to_integer()
        self.bone[1] = self.bone[1].to_integer()

        for a in self.arrow:
            a = a.to_integer()

        for child in self.child_bones:
            child.to_integer()


    def print_all_child(self):
        self.print_info()
        for child in self.child_bones:
            child.print_all_child()

    def mirror(self):
        self.bone[0].y = -self.bone[0].y
        self.bone[1].y = -self.bone[1].y

        self.rect.pos[1] = self.rect.size[1] * 2

        self.arrow[0].y = -self.arrow[0].y
        self.arrow[1].y = -self.arrow[1].y
        self.arrow[2].y = -self.arrow[2].y

        for child in self.child_bones:
            child.mirror()

    def offset(self, offset_x, offset_y):
        self.bone[0].x = self.bone[0].x + offset_x
        self.bone[0].y = self.bone[0].y + offset_y
        self.bone[1].x = self.bone[1].x + offset_x
        self.bone[1].y = self.bone[1].y + offset_y

        self.rect.pos[0] = self.rect.pos[0] + offset_x
        self.rect.pos[1] = self.rect.pos[1] + offset_y

        self.arrow[0].x = self.arrow[0].x + offset_x
        self.arrow[0].y = self.arrow[0].y + offset_y
        self.arrow[1].x = self.arrow[1].x + offset_x
        self.arrow[1].y = self.arrow[1].y + offset_y
        self.arrow[2].x = self.arrow[2].x + offset_x
        self.arrow[2].y = self.arrow[2].y + offset_y

        for child in self.child_bones:
            child.offset(offset_x, offset_y)

    def get_width(self):
        if self.direction == 'vertical':
            if self.level == 1:
                return const.WIDTH * 3 - 5
            else:
                return const.WIDTH - 5
        else:
            return self.bone[1].x - self.bone[0].x
