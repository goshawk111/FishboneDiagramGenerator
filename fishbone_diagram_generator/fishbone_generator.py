
"""
Fishbone generation module
"""
import fishbone_diagram_generator.const as const
from fishbone_diagram_generator.fishbone import Pos
from fishbone_diagram_generator.fishbone import FishBone
import math


class FishBoneGenerator():
    """ Fishbone generation class """
    def __init__(self, xml_loader):
        self.xml_loader = xml_loader
        self.main_bone = [Pos(0, 0), Pos(0, 0)]
        self.sub_bones = []
        self.is_create = False
        self.text = xml_loader.get_effect()
        self.horizontal_min_x = 0
        self.vertical_min_y = 0
        self.min_x = 0
        self.min_y = 0
        self.direction = xml_loader.get_diagram_param('direction')

    def create(self):
        root = self.xml_loader.get_factor()
        for child in root:
            self.sub_bones.append(self.generate_sub_bone(child))

        index = 0
        offset_up_x = 0
        offset_down_x = 0
        for sub_bone in self.sub_bones:
            if index % 2 == 0:
                sub_bone.offset(sub_bone.rect.size[0], sub_bone.rect.size[1])

                sub_bone.offset(
                    const.DIAGRAM_X - sub_bone.rect.size[0] - offset_up_x, const.DIAGRAM_Y - sub_bone.rect.size[1] - (const.MAIN_BONE_WIDTH / 2 + 1))
                offset_up_x = offset_up_x + sub_bone.rect.size[0]

            else:
                sub_bone.mirror_y()
                sub_bone.offset(sub_bone.rect.size[0], sub_bone.rect.size[1])
                sub_bone.offset(
                    const.DIAGRAM_X - sub_bone.rect.size[0] - offset_down_x, const.DIAGRAM_Y - sub_bone.rect.size[1] + (const.MAIN_BONE_WIDTH / 2 + 1))
                offset_down_x = offset_down_x + sub_bone.rect.size[0]

            index = index + 1

        offset_x = max(offset_up_x, offset_down_x)

        # print(offset_x)

        self.main_bone[0].x = const.DIAGRAM_X - offset_x
        self.main_bone[0].y = const.DIAGRAM_Y
        self.main_bone[1].x = const.DIAGRAM_X + const.HORIZONTAL_MARGIN
        self.main_bone[1].y = const.DIAGRAM_Y

        self.update_direction(self.direction)

        self.is_create = True

    def update_direction(self, direction):
        if direction == 'left':
            origin_x = (self.main_bone[0].x + self.main_bone[1].x) / 2

            for mb in self.main_bone:
                dx = mb.x - origin_x
                mb.x = origin_x - dx

            for sub_bone in self.sub_bones:
                sub_bone.mirror_x(origin_x)

    def find_horizontal_min_x(self, bone):
        if bone.direction == 'horizontal':
            if bone.bone[0].x < self.horizontal_min_x:
                self.horizontal_min_x = bone.bone[0].x
        if bone.direction == 'vertical':
            if bone.bone[1].x < self.horizontal_min_x:
                self.horizontal_min_x = bone.bone[1].x

        for child in bone.child_bones:
            self.find_horizontal_min_x(child)

    def find_vertical_min_y(self, bone):
        # if bone.direction == 'vertical':
        if bone.bone[0].y < self.vertical_min_y:
            self.vertical_min_y = bone.bone[0].y

        for child in bone.child_bones:
            self.find_vertical_min_y(child)

    def find_min_x(self, bone):
        if bone.parent is not None:
            for child in bone.parent.child_bones:
                if child.bone[0].x < self.min_x:
                    self.min_x = child.bone[0].x

        if bone.bone[0].x < self.min_x:
            self.min_x = bone.bone[0].x

        for child in bone.child_bones:
            self.find_min_x(child)

    def find_min_y(self, bone):
        if bone.parent is not None:
            for child in bone.parent.child_bones:
                if child.bone[0].y < self.min_y:
                    self.min_y = child.bone[0].y

        if bone.bone[0].y < self.min_y:
            self.min_y = bone.bone[0].y

        for child in bone.child_bones:
            self.find_min_y(child)

    def add_vertical_bone(self, bone):
        if bone.direction == 'vertical':
            if bone.level == 1:
                add_bone = const.VERTICAL_BONE_ADD * 8
            else:
                add_bone = const.VERTICAL_BONE_ADD
            deg = const.DEG
            offset_x = math.tan(math.radians(deg)) * add_bone
            bone.bone[0].y = bone.bone[0].y - add_bone
            bone.bone[0].x = bone.bone[0].x - offset_x

        for child in bone.child_bones:
            self.add_vertical_bone(child)

    def update_arrow(self, bone):
        bone.calc_arrow()

        for child in bone.child_bones:
            self.update_arrow(child)

    def update_rect(self, bone):
        self.min_x = 0
        self.min_y = 0

        self.find_min_x(bone)
        self.find_min_y(bone)

        bone.rect.pos[0] = self.min_x
        bone.rect.pos[1] = self.min_y
        bone.rect.size[0] = abs(self.min_x)
        bone.rect.size[1] = abs(self.min_y)

    def update_bone_length(self, bone):

        self.min_x = 0
        self.min_y = 0

        self.find_min_x(bone)
        self.find_min_y(bone)

        if bone.direction == 'horizontal':
            bone.bone[0].x = self.min_x

        if bone.direction == 'vertical':
            deg = const.DEG
            diff = bone.bone[0].y - self.min_y
            offset_x = math.tan(math.radians(deg)) * diff
            bone.bone[0].y = self.min_y
            bone.bone[0].x = bone.bone[0].x - offset_x

        for child in bone.child_bones:
            self.update_bone_length(child)

    def get_insert_bone_pos(self, bone):
        if bone.direction == 'vertical':
            if len(bone.parent.child_bones) == 0:
                return bone.parent.bone[1].x

            offset_x = const.HORIZONTAL_MARGIN
            self.horizontal_min_x = bone.parent.bone[1].x - offset_x
            for child in bone.parent.child_bones:
                self.find_horizontal_min_x(child)

            return self.horizontal_min_x

        if bone.direction == 'horizontal':
            if len(bone.parent.child_bones) == 0:
                return bone.parent.bone[1].y

            self.vertical_min_y = bone.parent.bone[1].y - const.VERTICAL_MARGIN
            for child in bone.parent.child_bones:
                self.find_vertical_min_y(child)

            return self.vertical_min_y

    def get_sub_child_bone(self, node, bone):

        if node.tag != 'Topics':
            return False

        child_bone = FishBone(bone)
        child_bone.text = node.attrib['text']

        height = const.HEIGHT
        width = const.WIDTH
        deg = const.DEG

        if child_bone.direction == 'vertical':
            insert_x = self.get_insert_bone_pos(child_bone)

            offset_x = math.tan(math.radians(deg)) * height
            child_bone.bone[1] = Pos(
                insert_x - const.HORIZONTAL_MARGIN, bone.bone[1].y)
            child_bone.bone[0] = Pos(
                insert_x - const.HORIZONTAL_MARGIN - offset_x, bone.bone[1].y - height)

        else:
            insert_y = self.get_insert_bone_pos(child_bone)

            offset_x = math.tan(math.radians(
                deg)) * const.VERTICAL_MARGIN + math.tan(math.radians(deg)) * abs(insert_y - bone.bone[1].y)

            child_bone.bone[1] = Pos(bone.bone[1].x - offset_x,
                                     insert_y - const.VERTICAL_MARGIN)
            child_bone.bone[0] = Pos(child_bone.bone[1].x - width,
                                     insert_y - const.VERTICAL_MARGIN)

        bone.child_bones.append(child_bone)
        # child_bone.print_info()

        for child in node:
            self.get_sub_child_bone(child, child_bone)

    def generate_sub_bone(self, root):
        sub_bone = FishBone(None)

        if root.tag != 'Factor':
            return False

        sub_bone.text = root.attrib['text']

        for child in root:
            self.get_sub_child_bone(child, sub_bone)

        height = const.HEIGHT
        deg = const.DEG

        offset_x = math.tan(math.radians(deg)) * height
        sub_bone.bone[0] = Pos(-offset_x, -height)
        sub_bone.bone[1] = Pos(0, 0)

        self.update_bone_length(sub_bone)
        self.add_vertical_bone(sub_bone)
        self.update_rect(sub_bone)
        self.update_arrow(sub_bone)

        # sub_bone.print_all_child()

        return sub_bone
