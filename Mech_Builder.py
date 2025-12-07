from copy import deepcopy

import pygame as pg
import os
import math
import time

# ----------------------------------------------------------------------------------------------------------------------
# Manufacturer OS part compatibility
# ----------------------------------------------------------------------------------------------------------------------
#                                           -------|-------|-------|-------|-------|-------|-------|-------|
#   Manufacturer                OS          SWM     Socrate Toolkit Nest    EW      LR      spe     FMB
#   Steel Wing Metalworks       DiamondOS   High    Low     Mid     Low     Mid     Mid     Mid     Mid     LMH 251
#   Socrates                    Plato       Low     High    Mid     Low     High    Mid     Low     Low     LMH 422
#   Toolkit Manufacturing       Lx OS       Mid     Low     High    Mid     Low     Mid     Mid     Mid     LMH 251
#   Nest                        <>          Low     Low     Mid     High    Low     Low     Low     Mid     LMH 521
#   <Electronic warfare>        <>          Mid     Mid     Low     Low     High    Mid     High    Low     LMH 332
#   <Long range>                Arda        Mid     Mid     Mid     Low     Low     High    Low     Mid     LMH 341
#   Special                     Saucisson   Mid     Mid     Low     Low     Mid     Low     High    Low     LMH 431
#                               Soulless    Low     Low     Low     Low     Low     Low     High    High    LMH 602
#   FMB                         <>          Low     Low     Mid     Mid     Low     Low     Low     High    LMH 521
#                                           LMH 441 LMH 531 LMH 351 LMH 621 LMH 522 LMH 441 LMH 423 LMH 342

# ----------------------------------------------------------------------------------------------------------------------
# Drivers
# ----------------------------------------------------------------------------------------------------------------------
# Name                          Manu.       Cost    Effect
#   Compatibility               *           High    Raise OS with manufacturer compatibility level of the driver by 1
#                                                     Can't go over High (3)
#   Energy Weapons              Socrates    Mid     Energy weapons made by Socrates act as they have max compatibility

# ----------------------------------------------------------------------------------------------------------------------
# Parts stat info
# ----------------------------------------------------------------------------------------------------------------------
# Universal
#   Weight                  How much weight the part has
#   E Cost                  How much it takes from the Gen Supply
#   H Cost                  Reduces cooling. If the cooling gets too low. You'll overheat
#   H Capacity              How much heat the part can store before causing issues
#   P Cost                  How much it uses from the Computer's Process. Power
#   Balance                 Offset that gets applied to the center of the MA, makes it lean in the direction of movement
#                               or stumble if high, and it goes too fast
#   Manu. Compatibility     Affect how well parts perform with the OS

# Frame
#   General
#       Armour points       How much health the piece adds to the MA
#       Ke def              Damage reduction for Kinetic damage
#       Bl def              Damage reduction for Blast damage
#       En def              Damage reduction for Energy damage
#       Camera              If it has cameras or not and it's quality, affects targeting range
#   Head
#       Radar range         Area covered by the radar signal, used by missiles. Used for mini map
#       Radar refresh       Rate at which radar signal is sent, used by missiles. Used for mini map
#       H Sensor            Detects heat.
#       R Sensor            Detects other radar signals.
#       Firing Stability    Affects the rate it takes for a weapon to go back to where you're aiming
#       ECM def             Reduces ECM effects
#   Torso
#       Gen Efficacy        Modifier to Gen Output and Gen Supply
#       Rad Efficacy        Modifier to H Capacity and Cooling rate
#       Bst Efficacy        Modifier to Boost Accel and Boost E cost
#       Stability           Affects the threshold of stumbling
#       Firing Stability    Affects the rate it takes for a weapon to go back to where you're aiming
#       Torso Feature       Special feature unique to the Torso. Require Mid compatibility
#   Arm (Left, Right)
#       Arm Weight Cap      How much weight each arm can hold
#       Handling            How quick the arms can move weapons
#       Recoil Control      How much recoil the arms are able to absorb. If too low some weapons can't be shot.
#       Aim Mod             How much spread is reduced by the arm
#       Firing Stability    Affects the rate it takes for a weapon to go back to where you're aiming
#   Leg
#       Weight Cap          How much weight the whole MA can hold
#       Turn rate           How quickly the MA turns
#       Walk speed          Top speed of MA in walk mode, adjusted with total weight
#       Walk accel          Rate at which speed is gained in walk mode, adjusted with total weight
#       Stability           Affects the threshold of stumbling
#       Firing Stability    Affects the rate it takes for a weapon to go back to where you're aiming

# Internals
#   Computer/FCS
#       Process. Power      How much P Cost the whole MA can take. Excess decreases the Boot Up time
#       Memory Supply       How much drivers can be installed on the MA
#       Target Acq. Spd.    How fast the MA can lock onto a target
#       Targeting Range     Limit on how far a target can be locked on
#       M. Target Acq. Spd. How fast the MA can lock onto a target for missiles
#       M. Targeting Range  Limit on how far a target can be locked on for missiles
#       M. Target Count     Limit on how many targets can be locked on for missiles
#       Power-On time       Affects how long the start-up sequence lasts
#       ECM def             Reduces ECM effects
#   OS
#       Malfunction rate    How often the computer might crash. Compatibility is HEAVILY affecting this
#       Features            Special effects the OS gives to the MA. Helpful for weapons.
#       Boot Up time        Affects how long the start-up sequence lasts
#   Generator
#       Gen Output          How much energy is generated
#       Gen Capacity        How much energy the generator can hold
#       Gen Supply          How much E Cost the whole MA can take
#       H Warning Zone      If heat over that threshold, Gen Output is reduced
#       Restart time        Affects how long the start-up sequence lasts
#   Radiator
#       H Capacity          How much heat the MA can take before having to make an emergency shutdown
#       Cooling rate        How much heat is lost constantly
#       Heat transfer rate  How fast heat is transferred from the mech to the radiator
#       Reliability         Affects the speed at which heat is lost when the mech is using took much energy
#   Boosters
#       Hover speed         Top speed of MA in hover mode, adjusted with total weight
#       Boost Accel         Rate at which speed is gained in hover and boost mode, adjusted with total weight
#       Boost E cost        How much energy is drained when boosting
#       Boost H cost        How much heat is added when boosting
#       Melee boost         How far melee lunges can send the MA forward, affected by the weapon
#       Hover opt cap       If this number is exceeded, hovering will cause the mech to start overheating

# ----------------------------------------------------------------------------------------------------------------------
# Weapons
# ----------------------------------------------------------------------------------------------------------------------
# Gen
#       Dmg Type            Which damage type it uses (Ke, Bl, En)
#       Weapon type         Which weapon type it is
#                               Gun         Rifle, Machine Gun, Sniper, Shotgun, Gatling, Handgun. Railgun, Cannon,
#                               Explosive   Missile L., Rocket L., Grenade L.
#                               Misc.       Blade, Flamethrower, Battery, Radar, Storage, Cooler, ECM, Shield, Drone
#       Damage amount       How much damage is dealt. If any
#       Heat increase       How much heat is added when using the weapon
#       Fire rate           How fast it takes for the weapon to do its stuff.
#       Accuracy
#       Magazine size
#       Ammo pool
#       Recoil
# Gun
#   General                 (Rifle, Machine Gun, Sniper, Handgun, Cannon)
#   Shotgun
#       Pellet count        How many pellets is shot by the shotgun
#   Gatling
#       Heat up rate        Rate at which the gatling heats up and stop firing. (unrelated to the mech heat)
#   Railgun
#       Charge up rate      .
# Explosive
#   General                 (Rocket L., Grenade L.)
#       Explosion radius    How big the explosion is.
#   Missile L.
#       Manoeuvrability     How fast the missile can change its heading
#       Missile type        Add extra behaviours to the missile.
#                               Basic,      just projectile that track their target
#                               Proximity   explodes before hitting the target, better hit chances
#                               Scatter
#                               Siege       stays in place before boosting toward the target
# Misc.
#   Blade
#   Flamethrower
#       Output Temperature  The rate at which it increases the heat of the target
#   Battery (only one model)
#   Radar
#       Radar range         Area covered by the radar signal, used by missiles. Used for mini map
#       Radar refresh       Rate at which radar signal is sent, used by missiles. Used for mini map
#       H Sensor            Detects heat.
#       R Sensor            Detects other radar signals.
#       ECM def             Reduces ECM effects
#   Storage (only one model)
#   Cooler (only one model)
#   ECM
#   Shield
#   Drone

# ----------------------------------------------------------------------------------------------------------------------
# Mission
# ----------------------------------------------------------------------------------------------------------------------
#   1A  2A  3A  4A  5A  6A  Loyalty (Stay with the colony, Fight Bloodhound)
#       2B  3B  4B  5B  6B  The Nest  (Follow Raven)
#           3C  4C  5C  6C  Free Actor (Escape by yourself)
#               4D  5D  6D  (Chased by Venator-Custos)
#                   5E      Escape (Follow Valais)
#                   5F  6F  Destruction (Follow Geneva)
# 1A
#   Defend Colony       2A
#   Attack Colony       2B
# 2A
#   .                   3A
#   .                   3B
# 3A
#   .                   4A
#   .                   4B
# 4A
#   .                   5A
#   .                   5B
# 5A
#   .                   6A
#   .                   6B
# 6A
#   Destroy Depot       Ending A: Loyalty, Caster 6 becomes a feared mercenary
# 2B
#   .                   3B
#   .                   3C
# 3B
#   .                   4B
#   .                   4C
# 4B
#   Complete Objective          5B
#   Abandon the unit            5C
# 5B
#   Complete Objective          6B
# 6B
#   Defeat Raven                Ending B: The Nest, Caster 6 joins the Nest
# 3C
#   .                   4B
#   .                   4C
#   .                   4D
# 4C
#   .                   5C
#   .                   5D
#   .                   5E
# 5C
#   Evade Anti-Deserter Unit    6C
# 6C
#   Defeat Elevator defenses    Ending C: Free Actor,
# 4D
#   .                           5D
#   Follow Valais               5E
#   Follow Geneva               5F
# 5D
#   Beat Venator-Custos         Ending D:
# 5E
#   Reach Space elevator        Ending E: Escape, Caster 6 along the rest of the pirates dies
# 5F
#   Destroy Settlement          6F
# 6F
#   Beat Valais, Bloodhound,
#   Raven & Venator-Custos      Ending F: Destruction, Caster 6 becomes "The Biggest Monster known to the world"


pg.init()

# import Fun


def get_image(img):
    return pg.image.load(os.path.join(img)).convert_alpha()


def swap(swap_img, old_colour, new_colour):
    # To swap with and have transparency
    # place (0, 0, 0) at the end of old_colour and (0, 0, 0, 0) at the end of new_colour
    # sawp_img should not have transparency

    # Based on DaFluffyPotato code
    # Changes : the 2 function have been fused, the function is more flexible with inputs
    for colour_swap in range(len(old_colour)):
        img_copy = pg.Surface(swap_img.get_size())
        img_copy.fill((0, 0, 0))
        img_copy.fill(new_colour[colour_swap])
        swap_img.set_colorkey(old_colour[colour_swap])
        img_copy.blit(swap_img, (0, 0))
        swap_img = img_copy
    swap_img.set_colorkey((0, 0, 0))
    return swap_img



pg.display.set_mode((500, 500))

MAX_MECH_HEIGHT = 96
HEIGHT_DIFF = 0.7
pos = [100, 125]

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


def make_part(sprite_list, part_palette, part_type, unbuilt_mech):
    offset = [0, 0, 0]
    p = [0, 0, 0]
    if part_type == "Torso":
        offset = get_off_set_points(unbuilt_mech["Leg"]["Sprite"], sprite_list, (255, 0, 0))

    # There to simplify code
    if part_type not in ["Torso", "Leg"]:
        p = get_off_set_points(unbuilt_mech["Leg"]["Sprite"], unbuilt_mech["Torso"]["Sprite"], (255, 0, 0))
    # Get real offset
    if part_type == "Head":
        p2 = get_off_set_points(unbuilt_mech["Torso"]["Sprite"], sprite_list, (255, 0, 255))
        offset = [p2[0]+p[0], p2[1]+p[1], p2[2] + p[2]]
    if part_type == "Arm L":
        p3 = get_off_set_points(unbuilt_mech["Torso"]["Sprite"], sprite_list, (0, 255, 0), check_for_right=False)
        offset = [p3[0]+p[0], p3[1]+p[1], p3[2] + p[2]]
    if part_type == "Arm R":
        p4 = get_off_set_points(unbuilt_mech["Torso"]["Sprite"], sprite_list, (0, 255, 0), check_for_right=True)
        offset = [p4[0]+p[0], p4[1]+p[1], p4[2] + p[2]]
    if part_type == "Arm Shoulder R":
        p4 = get_off_set_points(unbuilt_mech["Torso"]["Sprite"], unbuilt_mech["Arm R"]["Sprite"], (0, 255, 0), check_for_right=True)
        p5 = get_off_set_points(unbuilt_mech["Arm R"]["Sprite"], sprite_list, (0, 255, 255))
        offset = [p5[0]+p4[0], p5[1]+p4[1], p5[2] + p[2] + p4[2]]
    if part_type == "Arm Shoulder L":
        p4 = get_off_set_points(unbuilt_mech["Torso"]["Sprite"], unbuilt_mech["Arm L"]["Sprite"], (0, 255, 0), check_for_right=False)
        p6 = get_off_set_points(unbuilt_mech["Arm L"]["Sprite"], sprite_list, (0, 255, 255))
        offset = [p6[0]+p4[0]+p[0], p6[1]+p4[1]+p[1], p6[2] + p[2] + p4[2]]
    if part_type == "Wpn L":
        p4 = get_off_set_points(unbuilt_mech["Torso"]["Sprite"], unbuilt_mech["Arm L"]["Sprite"], (0, 255, 0), check_for_right=False)
        p7 = get_off_set_points(unbuilt_mech["Arm L"]["Sprite"], sprite_list, (255, 255, 0))
        offset = [p7[0]+p4[0]+p[0], p7[1]+p4[1]+p[1], p7[2] + p[2] + p4[2]]
    if part_type == "Wpn R":
        # p = get_off_set_points(unbuilt_mech["Leg"]["Sprite"], unbuilt_mech["Torso"]["Sprite"], (255, 0, 0))
        p3 = get_off_set_points(unbuilt_mech["Torso"]["Sprite"], unbuilt_mech["Arm R"]["Sprite"], (0, 255, 0), check_for_right=True)
        p7 = get_off_set_points(unbuilt_mech["Arm R"]["Sprite"], sprite_list, (255, 255, 0))
        offset = [p7[0]+p3[0]+p[0], p7[1]+p3[1]+p[1], p7[2] + p[2] + p3[2]]
    if part_type == "Shoulder R":
        p4 = get_off_set_points(unbuilt_mech["Torso"]["Sprite"], sprite_list, (0, 255, 255), check_for_right=True)
        offset = [p4[0]+p[0], p4[1]+p[1], p4[2] + p[2]]
    if part_type == "Shoulder L":
        p4 = get_off_set_points(unbuilt_mech["Torso"]["Sprite"], sprite_list, (0, 255, 255), check_for_right=False)
        offset = [p4[0] + p[0], p4[1] + p[1], p4[2] + p[2]]

    return {"Sprite": sprite_list, 'h2': len(sprite_list), "offset": offset, "palette": part_palette.copy()}


def distance_between(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def move_with_vel_angle(base_pos, vel, angle):
    # I could switch math.pi to 3
    angle = angle * math.pi / 180
    # return [base_pos[0] - vel * math.sin(angle), base_pos[1] - vel * math.cos(angle)]  # Evil
    return [base_pos[0] - vel * math.cos(angle), base_pos[1] - vel * math.sin(angle)]


def timeme(method):
    # Keep this for testing, use it as a decorator
    def wrapper(*args, **kw):
        startTime = int(time.time_ns())
        # startTime = datetime.datetime.now().microsecond / 1000
        result = method(*args, **kw)
        endTime = int(time.time_ns())
        # endTime = datetime.datetime.now().microsecond / 1000
        print(endTime - startTime)
        return result

    return wrapper


class Mech:
    def __init__(self, mech_parts, mech_palette, pos=pos):
        self.mech_parts = {}
        self.mech_palette = mech_palette
        for part_to_add in mech_parts:
            self.mech_parts.update(
                {part_to_add["Type"]: make_part(part_to_add["Sprite"], self.mech_palette[part_to_add["Type"]], part_to_add["Type"], self.mech_parts)})
        self.backup_mech_copy = deepcopy(self.mech_parts)
        for e in self.mech_parts:
            self.mech_parts = paint_single_part(self.mech_parts.copy(), e, self.backup_mech_copy .copy())

        self.mech_sprite_stack = []
        for i in range(MAX_MECH_HEIGHT):
            new_layer = []
            for e in self.mech_parts:
                # It should be possible to store the sprites in a way that makes this check useless.
                # Which would help performances
                if self.mech_parts[e]["offset"][2] <= i < self.mech_parts[e]["offset"][2] +self.mech_parts[e]["h2"]:
                    num = i - self.mech_parts[e]["offset"][2]
                    sprite = self.mech_parts[e]["Sprite"][num]
                    new_layer.append([sprite, self.mech_parts[e]["offset"][0], self.mech_parts[e]["offset"][1]])
            # if not new_layer:
            #     print(i)
            self.mech_sprite_stack.append(new_layer)
        self.pos = pos

    # @timeme
    def draw(self, win, t):
        angle = t // 4
        win.fill((32, 32, 32))
        mech_surface = pg.Surface((200, 200))

        height_mod = 1  # How to cheat at optimisation. Do less.
        for count, layer in enumerate(self.mech_sprite_stack):
            draw_height = count * height_mod
            layer_surf = empty_mech_surf.copy()
            for layer_info in layer:
                sprite_layer = layer_info[0]
                layer_surf.blit(sprite_layer, [mech_surf_size // 2 - sprite_layer.get_width() // 2 + layer_info[1],
                                               mech_surf_size // 2 - sprite_layer.get_height() // 2 + layer_info[2]])

            layer_surf = pg.transform.rotate(layer_surf, angle)
            mech_surface.blit(layer_surf,
                              (self.pos[0] - layer_surf.get_width() // 2,
                               self.pos[1] - layer_surf.get_height() // 2 - HEIGHT_DIFF * draw_height
                               # * (1 +math.sin(t/20))
                               ))

        mech_surface = pg.transform.scale_by(mech_surface, 2.5)
        win.blit(mech_surface, (0, 0))


def fucks(fps=60):
    clock = pg.time.Clock()
    win = pg.display.set_mode((500, 500))
    t = 1
    rendered_mech = Mech(
    [
        # {"Type": "Leg", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/LT-Fitch.png'), 65)},
        # {"Type": "Leg", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/LQ-Forbes.png'), 65)},
        {"Type": "Leg", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/LB-Mantle.png'), 26)},
        # {"Type": "Leg", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/LQ-Igneous.png'), 85)},

        {"Type": "Torso", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/TO-Igneous.png'), 26)},
        # {"Type": "Torso", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/TO-Orion.png'), 64)},
        # {"Type": "Torso", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/TO-Forbes.png'), 49)},

        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Bedrock.png'), 13)},
        {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Igneous.png'), 12)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Sediment.png'), 10)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Mantle.png'), 12)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Knipp.png'), 12)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Paio.png'), 13)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Skull.png'), 21)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Suprematie.png'), 13)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Lauriers.png'), 11)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Victoire.png'), 8)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Kocc Barma.png'), 12)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-T. More.png'), 16)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Descartes.png'), 10)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Diogenes.png'), 14)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Kant.png'), 10)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Bits.png'), 11)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-DOS.png'), 10)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Barad-Dur.png'), 10)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Rohan.png'), 13)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Shelob.png'), 14)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Forbes.png'), 10)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Fitzinger.png'), 9)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Fitch.png'), 13)},
        # {"Type": "Head", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HD-Orion.png'), 17)},

        {"Type": "Arm L", "Sprite": invert_sprite_stack('Sprites/Mech parts/AM-Igneous.png', 31)},
        # {"Type": "Arm L", "Sprite": invert_sprite_stack('Sprites/Mech parts/AM-Paio.png', 30)},
        # {"Type": "Arm L", "Sprite": invert_sprite_stack('Sprites/Mech parts/AM-Kocc Barma.png', 31)},
        # {"Type": "Arm L", "Sprite": invert_sprite_stack('Sprites/Mech parts/AM-Orion.png', 27)},

        # {"Type": "Arm L", "Sprite": invert_sprite_stack('Sprites/Mech parts/AW-RL-Brauer.png', 32)},
        # {"Type": "Arm L", "Sprite": invert_sprite_stack('Sprites/Mech parts/AW-GT-Lopolith.png', 64)},
        # {"Type": "Arm L", "Sprite": invert_sprite_stack('Sprites/Mech parts/AW-BL-Fall.png', 15)},

        # {"Type": "Arm R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/AM-Orion.png'), 27)},
        # {"Type": "Arm R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/AM-Igneous.png'), 31)},
        # {"Type": "Arm R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/AM-Paio.png'), 30)},
        # {"Type": "Arm R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/AM-Kocc Barma.png'), 31)},

        # {"Type": "Arm R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/AW-RL-Brauer.png'), 32)},
        {"Type": "Arm R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/AW-GT-Lopolith.png'), 64)},
        # {"Type": "Arm R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/AW-BL-Fall.png'), 15)},

        {"Type": "Wpn L", "Sprite": invert_sprite_stack('Sprites/Mech parts/BL-Magma.png', 20)},
        # {"Type": "Wpn R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/HG-Oken.png'), 14)},
        # {"Type": "Wpn R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/BL-Magma.png'), 20)},

        # {"Type": "Arm Shoulder L", "Sprite": invert_sprite_stack('Sprites/Mech parts/ML-Hadean.png', 15)},
        # {"Type": "Arm Shoulder L", "Sprite": invert_sprite_stack('Sprites/Mech parts/CA-.png', 10)},

        # {"Type": "Arm Shoulder R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/CA-.png'), 10)},
        # {"Type": "Arm Shoulder R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/ML-Hadean.png'), 15)},

        # {"Type": "Shoulder L", "Sprite": invert_sprite_stack('Sprites/Mech parts/ML-Hadean.png', 15)},
        {"Type": "Shoulder L", "Sprite": invert_sprite_stack('Sprites/Mech parts/CA-.png', 10)},

        # {"Type": "Shoulder R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/CA-.png'), 10)},
        {"Type": "Shoulder R", "Sprite": get_sprite_stack_list(get_image('Sprites/Mech parts/ML-Hadean.png'), 15)},
    ],
        # full_mech_palette,
        bloodhound_palette
        # default_palette,
    )
    delta_time = 0
    while True:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                quit()

        keys = pg.key.get_pressed()

        # Draw
        # for x in range(1):
        rendered_mech.draw(win, t)
        # menu_logic.draw(WIN, [500, 0])
        pg.display.update()
        # mod = math.cos(t/6) * 40
        delta_time = clock.tick(fps)
        t += 1.75 * delta_time / 17
        # print(delta_time)

        # print(CLOCK.get_fps())


fucks()
