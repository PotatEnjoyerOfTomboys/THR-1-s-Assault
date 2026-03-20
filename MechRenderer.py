import pygame as pg
import math

from copy import deepcopy
from Fun import get_image, swap, distance_between, angle_between, move_with_vel_angle


MAX_MECH_HEIGHT = 96
HEIGHT_DIFF = 0.7

mech_surf_size = 96 # Making sure this number is as small as possible helps a lot with performances
mech_surf_size_halved = mech_surf_size // 2
empty_mech_surf = pg.Surface((mech_surf_size, mech_surf_size))

empty_mech_surf_copy = pg.Surface((mech_surf_size, mech_surf_size))
empty_mech_surf_copy.fill((0, 0, 0))
empty_mech_surf_copy.fill((0, 0, 0, 0))
empty_mech_surf.set_colorkey((0, 0, 0))
empty_mech_surf_copy.blit(empty_mech_surf, (0, 0))
empty_mech_surf = empty_mech_surf_copy
empty_mech_surf.set_colorkey((0, 0, 0))
empty_mech_surf.convert_alpha()


def get_off_set_points(parent_img, current_img, colour, check_for_right=True):
    x, y, z = 0, 0, 0

    supa_break = False
    for p_z, s in enumerate(parent_img):
        s_copy = pg.Surface((mech_surf_size, mech_surf_size))
        s_copy.blit(s, [mech_surf_size//2-s.get_width() // 2, mech_surf_size//2-s.get_height() // 2])

        for p_x in range(s_copy.get_width()):
            for p_y in range(s_copy.get_height()):
                if s_copy.get_at((p_x, p_y)) == colour:
                    # w = 64 - s_copy.get_height() // 2
                    w = mech_surf_size//2
                    # w = 32
                    x, y, z = p_x - w, p_y - w, p_z

                    # add option to find left one instead
                    if check_for_right:
                        supa_break = True
                        break
            if supa_break: break
        if supa_break: break

    for p_z, s in enumerate(current_img):
        s_copy = s
        for p_x in range(s_copy.get_width()):
            for p_y in range(s_copy.get_height()):
                if s_copy.get_at((p_x, p_y)) == colour:
                    z = z - p_z
                    # w = 0
                    # w = 64
                    # w = 32
                    x -= s.get_width() // 2 * -1 + p_x
                    y -= s.get_height() // 2 * -1 + p_y
                    # x, y, z = x + p_x - w, y + p_y - w, z
                    return [x, y, z]
    #                 w = ((65 - s.get_height())//2)
    #                 return [(x - p_x - w), (y - p_y - w), z - p_z]
                    # return [p_x - x//2, p_y - y//2, z - p_z]

    return [x, y, z]


def paint(paint_mech, new_colours):
    for part in paint_mech:
        new_layers = []
        for sprite_layer in paint_mech[part]["Sprite"]:
            new_layers.append(
                swap(sprite_layer,
                 [(0, 0, 0), MECH_COL_1, MECH_COL_2, MECH_COL_3, MECH_ACCENT, MECH_LIGHT],
                 [(0, 0, 0, 0), new_colours[0], new_colours[1], new_colours[2], new_colours[3], new_colours[4]])
            )
        paint_mech[part]["Sprite"] = new_layers
    return paint_mech


def paint_single_part(paint_mech, part_id, copied_mech):
    new_layers = []
    new_colours = paint_mech[part_id]["palette"]
    # print(part["palette"])
    for sprite_layer in copied_mech[part_id]["Sprite"]:
        new_layers.append(
            swap(sprite_layer.copy(),
                 [(0, 0, 0), MECH_COL_1, MECH_COL_2, MECH_COL_3, MECH_ACCENT, MECH_LIGHT],
                 [(0, 0, 0, 0), new_colours[0], new_colours[1], new_colours[2], new_colours[3], new_colours[4]])
        )
    paint_mech[part_id]["Sprite"] = new_layers
    return paint_mech


def invert_sprite_stack(sprite_stack, height):
    return [pg.transform.flip(e, True, False) for e in get_sprite_stack_list(get_image(sprite_stack), height)]


get_sprite_stack_list = lambda img, height: [img.subsurface((0, img.get_height() - height * (x + 1), img.get_width(), height)).convert_alpha() for x in range(img.get_height()//height)]

igneous_palette = [[147, 118, 123], [103, 88, 85], [78, 55, 72], [44, 39, 47], [226, 103, 38]]
MECH_COL_1 = (185, 185, 185)
MECH_COL_2 = (127, 127, 127)
MECH_COL_3 = (100, 100, 100)
MECH_ACCENT = (55, 55, 55)
MECH_LIGHT = (226, 103, 38)
DEFAULT_PALETTE = [MECH_COL_1, MECH_COL_2, MECH_COL_3, MECH_ACCENT, MECH_LIGHT]
palette = [list(MECH_COL_1), list(MECH_COL_2), list(MECH_COL_3), list(MECH_ACCENT), list(MECH_LIGHT)]

default_palette = {
    "Leg": [            MECH_COL_1, MECH_COL_2, MECH_COL_3, MECH_ACCENT, MECH_LIGHT],
    "Torso": [          MECH_COL_1, MECH_COL_2, MECH_COL_3, MECH_ACCENT, MECH_LIGHT],
    "Head": [           MECH_COL_1, MECH_COL_2, MECH_COL_3, MECH_ACCENT, MECH_LIGHT],
    "Arm L": [          MECH_COL_1, MECH_COL_2, MECH_COL_3, MECH_ACCENT, MECH_LIGHT],
    "Arm R": [          MECH_COL_1, MECH_COL_2, MECH_COL_3, MECH_ACCENT, MECH_LIGHT],
    "Wpn L": [          MECH_COL_1, MECH_COL_2, MECH_COL_3, MECH_ACCENT, MECH_LIGHT],
    "Wpn R": [          MECH_COL_1, MECH_COL_2, MECH_COL_3, MECH_ACCENT, MECH_LIGHT],
    "Shoulder L": [     MECH_COL_1, MECH_COL_2, MECH_COL_3, MECH_ACCENT, MECH_LIGHT],
    "Shoulder R": [     MECH_COL_1, MECH_COL_2, MECH_COL_3, MECH_ACCENT, MECH_LIGHT],
    "Arm Shoulder L": [ MECH_COL_1, MECH_COL_2, MECH_COL_3, MECH_ACCENT, MECH_LIGHT],
    "Arm Shoulder R": [ MECH_COL_1, MECH_COL_2, MECH_COL_3, MECH_ACCENT, MECH_LIGHT],
}
full_mech_palette = {
    "Leg": [            [90, 53, 53], [126, 74, 74], [25, 25, 25], [44, 39, 47], [226, 103, 38]],
    "Torso": [          [126, 74, 74], [90, 53, 53], [90, 53, 53], [25, 25, 25], [226, 103, 38]],
    # "Head": [           [126, 74, 74], [126, 74, 74], [90, 53, 53], [44, 39, 47], [226, 103, 38]],
    "Head": [           [74, 74, 126], [196, 196, 196], [53, 53, 90], [44, 39, 47], [226, 103, 38]],
    "Arm L": [          [147, 118, 123], [103, 88, 85], [78, 55, 72], [44, 39, 47], [226, 103, 38]],
    "Arm R": [          [147, 118, 123], [103, 88, 85], [78, 55, 72], [44, 39, 47], [226, 103, 38]],
    "Wpn L": [          [147, 118, 123], [103, 88, 85], [78, 55, 72], [44, 39, 47], [226, 103, 38]],
    "Wpn R": [          [147, 118, 123], [103, 88, 85], [78, 55, 72], [44, 39, 47], [226, 103, 38]],
    "Shoulder L": [     [147, 118, 123], [103, 88, 85], [78, 55, 72], [44, 39, 47], [226, 103, 38]],
    "Shoulder R": [     [147, 118, 123], [103, 88, 85], [78, 55, 72], [44, 39, 47], [226, 103, 38]],
    "Arm Shoulder L": [ [147, 118, 123], [103, 88, 85], [78, 55, 72], [44, 39, 47], [226, 103, 38]],
    "Arm Shoulder R": [ [147, 118, 123], [103, 88, 85], [78, 55, 72], [44, 39, 47], [226, 103, 38]],
}

bloodhound_palette = {
    "Leg": [            [83, 69, 34], [27, 27, 27], [58, 29, 29], [17, 17, 17], [226, 103, 38]],
    "Torso": [          [115, 95, 48], [81, 40, 40], [37, 37, 37], [23, 23, 23], [226, 103, 38]],
    "Head": [           [141, 117, 58], [45, 45, 45], [99, 50, 50], [29, 29, 29], [249, 113, 42]],
    "Arm L": [          [128, 106, 53], [41, 41, 41], [90, 45, 45], [26, 26, 26], [226, 103, 38]],
    "Arm R": [          [128, 106, 53], [41, 41, 41], [90, 45, 45], [26, 26, 26], [226, 103, 38]],

    "Wpn L": [          [96, 96, 96], [48, 48, 48], [32, 32, 32], [16, 16, 16], [249, 113, 42]],

    "Wpn R": [          [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],

    "Shoulder L": [     [96, 96, 96], [48, 48, 48], [32, 32, 32], [16, 16, 16], [226, 103, 38]],
    "Shoulder R": [     [141, 117, 58], [99, 50, 50], [45, 45, 45], [29, 29, 29], [249, 113, 42]],

    "Arm Shoulder L": [ [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
    "Arm Shoulder R": [ [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
}

rigel_palette = {
    "Leg": [            [83, 69, 34], [27, 27, 27], [58, 29, 29], [17, 17, 17], [226, 103, 38]],
    "Torso": [          [120, 106, 53], [120, 106, 53], [116, 95, 67], [26, 26, 26], [226, 103, 38]],
    "Head": [           [133, 118, 59], [103, 81, 59], [116, 95, 67], [26, 26, 26], [226, 103, 38]],
    "Arm L": [          [133, 118, 59], [103, 81, 59], [116, 95, 67], [26, 26, 26], [226, 103, 38]],
    "Arm R": [          [133, 118, 59], [103, 81, 59], [116, 95, 67], [26, 26, 26], [226, 103, 38]],

    "Wpn L": [          [96, 96, 96], [48, 48, 48], [32, 32, 32], [16, 16, 16], [249, 113, 42]],

    "Wpn R": [          [96, 96, 96], [48, 48, 48], [32, 32, 32], [16, 16, 16], [249, 113, 42]],

    "Shoulder L": [     [96, 96, 96], [48, 48, 48], [32, 32, 32], [16, 16, 16], [226, 103, 38]],
    "Shoulder R": [     [141, 117, 58], [99, 50, 50], [45, 45, 45], [29, 29, 29], [249, 113, 42]],

    "Arm Shoulder L": [ [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
    "Arm Shoulder R": [ [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
}

all_mech = [
        # {"Type": "Leg", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/LR-Orion.png'), 26)},
        # {"Type": "Torso", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/TO-Orion.png'), 64)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Orion.png'), 17)},
        # {"Type": "Arm L", "Sprite": invert_sprite_stack('Sprites/Mech parts/AM-Rigel.png', 10)},
        # {"Type": "Arm R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/AM-Orion.png'), 27)},
        # {"Type": "Wpn R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/BL-Magma.png'), 20)},
    ]
bloodhound_mech = [
        {"Type": "Leg", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/LB-Mantle.png'), 26)},
        {"Type": "Torso", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/TO-Igneous.png'), 26)},
        {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Igneous.png'), 12)},
        {"Type": "Arm L", "Sprite": invert_sprite_stack('Sprites/Mech parts/AW-GT-Lopolith.png', 64)},
        {"Type": "Arm R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/AM-Igneous.png'), 31)},
        {"Type": "Wpn R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/BL-Magma.png'), 20)},
        {"Type": "Shoulder L", "Sprite": invert_sprite_stack('Sprites/Mech parts/CA-.png', 10)},
        {"Type": "Shoulder R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/ML-Hadean.png'), 15)},
    ]

rigel_mech = [
        # {"Type": "Leg", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/LR-Orion.png'), 26)},
        # {"Type": "Torso", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/TO-Orion.png'), 64)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Orion.png'), 17)},
        # {"Type": "Arm L", "Sprite": invert_sprite_stack('Sprites/Mech parts/AM-Rigel.png', 10)},
        # {"Type": "Arm R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/AM-Orion.png'), 27)},
    ]

def make_part(sprite_list, part_palette, part_type, unbuilt_mech):
    offset = [0, 0, 0]
    p = [0, 0, 0]
    draw_angle = 0

    owner = "Leg"
    if part_type == "Torso":
        offset = get_off_set_points(unbuilt_mech["Leg"]["Sprite"], sprite_list, (255, 0, 0))
        owner = "Leg"

    # There to simplify code
    if part_type not in ["Torso", "Leg"]:
        p = get_off_set_points(unbuilt_mech["Leg"]["Sprite"], unbuilt_mech["Torso"]["Sprite"], (255, 0, 0))
    # Get real offset
    if part_type == "Head":
        p2 = get_off_set_points(unbuilt_mech["Torso"]["Sprite"], sprite_list, (255, 0, 255))
        offset = [p2[0]+p[0], p2[1]+p[1], p2[2] + p[2]]
        owner = "Torso"
    if part_type == "Arm L":
        p3 = get_off_set_points(unbuilt_mech["Torso"]["Sprite"], sprite_list, (0, 255, 0), check_for_right=False)
        offset = [p3[0]+p[0], p3[1]+p[1], p3[2] + p[2]]
        owner = "Torso"
    if part_type == "Arm R":
        p4 = get_off_set_points(unbuilt_mech["Torso"]["Sprite"], sprite_list, (0, 255, 0), check_for_right=True)
        offset = [p4[0]+p[0], p4[1]+p[1], p4[2] + p[2]]
        owner = "Torso"
    if part_type == "Arm Shoulder R":
        p4 = get_off_set_points(unbuilt_mech["Torso"]["Sprite"], unbuilt_mech["Arm R"]["Sprite"], (0, 255, 0), check_for_right=True)
        p5 = get_off_set_points(unbuilt_mech["Arm R"]["Sprite"], sprite_list, (0, 255, 255))
        offset = [p5[0]+p4[0], p5[1]+p4[1], p5[2] + p[2] + p4[2]]
        owner = "Arm R"
    if part_type == "Arm Shoulder L":
        p4 = get_off_set_points(unbuilt_mech["Torso"]["Sprite"], unbuilt_mech["Arm L"]["Sprite"], (0, 255, 0), check_for_right=False)
        p6 = get_off_set_points(unbuilt_mech["Arm L"]["Sprite"], sprite_list, (0, 255, 255))
        offset = [p6[0]+p4[0]+p[0], p6[1]+p4[1]+p[1], p6[2] + p[2] + p4[2]]
        owner = "Arm L"
    if part_type == "Wpn L":
        p4 = get_off_set_points(unbuilt_mech["Torso"]["Sprite"], unbuilt_mech["Arm L"]["Sprite"], (0, 255, 0), check_for_right=False)
        p7 = get_off_set_points(unbuilt_mech["Arm L"]["Sprite"], sprite_list, (255, 255, 0))
        offset = [p7[0]+p4[0]+p[0], p7[1]+p4[1]+p[1], p7[2] + p[2] + p4[2]]
        owner = "Arm L"
    if part_type == "Wpn R":
        # p = get_off_set_points(unbuilt_mech["Leg"]["Sprite"], unbuilt_mech["Torso"]["Sprite"], (255, 0, 0))
        p3 = get_off_set_points(unbuilt_mech["Torso"]["Sprite"], unbuilt_mech["Arm R"]["Sprite"], (0, 255, 0), check_for_right=True)
        p7 = get_off_set_points(unbuilt_mech["Arm R"]["Sprite"], sprite_list, (255, 255, 0))
        offset = [p7[0]+p3[0]+p[0], p7[1]+p3[1]+p[1], p7[2] + p[2] + p3[2]]
        owner = "Arm R"
    if part_type == "Shoulder R":
        p4 = get_off_set_points(unbuilt_mech["Torso"]["Sprite"], sprite_list, (0, 255, 255), check_for_right=True)
        offset = [p4[0]+p[0], p4[1]+p[1], p4[2] + p[2]]
        owner = "Torso"
    if part_type == "Shoulder L":
        p4 = get_off_set_points(unbuilt_mech["Torso"]["Sprite"], sprite_list, (0, 255, 255), check_for_right=False)
        offset = [p4[0] + p[0], p4[1] + p[1], p4[2] + p[2]]
        owner = "Torso"

    return {"Sprite": sprite_list, 'h2': len(sprite_list), "offset": offset, "palette": part_palette.copy(), "Draw angle": draw_angle, "Owner": owner, "Child": []}


def blit_rotate(surf, image, pos, origin_pos, angle):
    # This is used to draw weapons
    # offset from pivot to center
    image_rect = image.get_rect(topleft=(pos[0] - origin_pos[0], pos[1] - origin_pos[1]))
    offset_center_to_pivot = pg.math.Vector2(pos) - image_rect.center

    # roatated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # rotated image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pg.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

    # rotate and blit the image
    surf.blit(rotated_image, rotated_image_rect)


class Mech:
    def __init__(self, mech_parts, mech_palette, pos):
        self.time = 0
        # This class is used to render mechs which have individual parts
        self.mech_parts = {}
        self.mech_palette = mech_palette
        for part_to_add in mech_parts:
            self.mech_parts.update(
                {part_to_add["Type"]: make_part(part_to_add["Sprite"], self.mech_palette[part_to_add["Type"]], part_to_add["Type"], self.mech_parts)})
        for p in self.mech_parts:
            if self.mech_parts[p]["Owner"]:
                self.mech_parts[self.mech_parts[p]["Owner"]]["Child"].append(p)

        for p in self.mech_parts:
            if self.mech_parts[p]["Owner"]:
                if self.mech_parts[p]["Child"]:
                    for c in self.mech_parts[p]["Child"]:
                        if c not in self.mech_parts[self.mech_parts[p]["Owner"]]["Child"]:
                            self.mech_parts[self.mech_parts[p]["Owner"]]["Child"].append(c)

        self.backup_mech_copy = deepcopy(self.mech_parts)
        for e in self.mech_parts:
            self.mech_parts = paint_single_part(self.mech_parts.copy(), e, self.backup_mech_copy .copy())

        self.mech_sprite_stack = []
        for i in range(MAX_MECH_HEIGHT):
            new_layer = []
            for e in self.mech_parts:
                if self.mech_parts[e]["offset"][2] <= i < self.mech_parts[e]["offset"][2] + self.mech_parts[e]["h2"]:
                    num = i - self.mech_parts[e]["offset"][2]
                    sprite = self.mech_parts[e]["Sprite"][num]
                    new_layer.append([sprite, self.mech_parts[e]])
            if new_layer:
                self.mech_sprite_stack.append(new_layer)
        self.pos = pos
        for p in self.mech_parts:
            print(p)
            for pp in self.mech_parts[p]:
                print(pp)
                print(self.mech_parts[p][pp])

        # {"Time": 0, "Angle Speed": 0}
        self.mech_animations = {
            "Leg": [],
            "Torso": [],
            "Head": [],
            "Arm L": [],
            "Arm R": [],
            "Wpn L": [],
            "Wpn R": [],
            "Arm Shoulder L": [],
            "Arm Shoulder R": [],
            "Shoulder L": [],
            "Shoulder R": [],
        }

    def animate(self):
        # Used to do animations that doesn't need different sprites

        for part in self.mech_parts:
            # self.mech_parts[part]["offset"] = move_with_vel_angle([0, 0], distance_between([0, 0], self.mech_parts[part]["offset"])*-1, self.mech_parts[part]["Draw angle"])
            # self.mech_parts[part]["offset"][0] -= self.mech_parts[self.mech_parts[part]["Owner"]]["offset"][0]
            # self.mech_parts[part]["offset"][1] -= self.mech_parts[self.mech_parts[part]["Owner"]]["offset"][1]
            if self.mech_animations[part]:
                info = self.mech_animations[part][0]
                info["Time"] -= 1

                # self.mech_parts[part]["offset"][0] +=
                # self.mech_parts[part]["offset"][1] +=
                self.mech_parts[part]["Draw angle"] += info["Angle Speed"]
                for child in self.mech_parts[part]["Child"]:
                    self.mech_parts[child]["Draw angle"] += info["Angle Speed"]
                    # Modify offset here
                    self.mech_parts[child]["offset"] = move_with_vel_angle(
                        self.mech_parts[part]["offset"],
                        distance_between(self.mech_parts[part]["offset"], self.mech_parts[child]["offset"]),
                        angle_between(self.mech_parts[child]["offset"], self.mech_parts[part]["offset"]) - info["Angle Speed"]
                    )
                if info["Time"] == 0:
                    self.mech_animations[part].pop(0)

    def reset_animations(self):
        for p in self.mech_parts:
            self.mech_parts[p]["Draw angle"] = 0
        self.mech_animations = {
            "Leg": [], "Torso": [], "Head": [],
            "Arm L": [], "Arm R": [],
            "Wpn L": [], "Wpn R": [],
            "Arm Shoulder L": [], "Arm Shoulder R": [],
            "Shoulder L": [], "Shoulder R": [],
        }

    def draw(self, win, angle):
        self.animate()  # Don't know where to put that
        mech_surface = win

        height_mod = 1.3  # This can be used to optimize the render but removing some layers of the sprite stack

        for count, layer in enumerate(self.mech_sprite_stack):
            draw_height = count * height_mod
            layer_surf = empty_mech_surf.copy()
            for layer_info in layer:
                sprite = layer_info[0]
                origin = [sprite.get_width() // 2 , sprite.get_height() // 2]

                blit_rotate(layer_surf, sprite,
                            [mech_surf_size // 2  + layer_info[1]["offset"][0],
                              mech_surf_size // 2  + layer_info[1]["offset"][1]],
                            origin,
                            layer_info[1]["Draw angle"])

            layer_surf = pg.transform.rotate(layer_surf, angle * -1 - 90) # This part could be replaced using the animation system, might look into it
            mech_surface.blit(layer_surf,
                              (self.pos[0] - layer_surf.get_width() // 2,
                               self.pos[1] - layer_surf.get_height() // 2 - HEIGHT_DIFF * draw_height
                               # * (1 + math.sin(self.time/20)*0.33) # Bouncy mode
                               ))
        self.time += 1