import pygame as pg
import random
import math
import sys

import Fun
import Bullets
import Skills
import Weapons

from Fun import none
from Event import MissionEvent, loss_of_apc, trigger_constant

class Entity:
    __slots__=['agro', 'agro_decrease_rate', 'ai_state', 'aim_angle', 'angle', 'animation_counter', 'is_target', 'armour', 'armour_break', 'bullets_shot', 'collision_box', 'control', 'controller_angle', 'controller_control', 'crit', 'cutscene_mode', 'damage_taken', 'dash_allowed', 'dash_charge_time', 'dash_cooldown', 'dash_iframes', 'dash_speed', 'did_agro_raise', 'direction_angle', 'draw_aim_line', 'draw_angle', 'draw_rotated_dist', 'draw_targeting_range', 'driving', 'force_draw', 'free_var', 'friction', 'func_act', 'func_draw', 'func_input', 'health', 'input', 'input_mode', 'is_ally', 'is_boss', 'is_player', 'is_targeted', 'is_targeting', 'max_armour', 'max_health', 'mouse_control', 'mouse_pos', 'name', 'no_shoot_state', 'og_info', 'on_death', 'order_builder', 'pathfinding_old_positions', 'pos', 'reloading', 'resistances', 'running', 'shooting', 'shot_allowed', 'skills', 'sound_mod', 'speed', 'sprites', 'standing_still', 'status', 'stealth_counter', 'stealth_mod', 'target', 'targeting_angle', 'targeting_range', 'team', 'thiccness', 'time', 'upgrades', 'vel', 'vel_max', 'walking', 'wall_hack', 'weapon', 'weapon_draw_dist']
    def __init__(self, info, team="Players", pos=[0, 0], start_angle=0):
        info = info.copy()
        self.og_info = info.copy()
        self.name = info["name"]
        self.team = team
        self.is_ally = False
        self.is_player = False
        self.is_boss = False
        self.crit = False

        # |Health and armour|-------------------------------------------------------------------------------------------
        self.max_health = info["health"]
        self.health = self.max_health
        self.max_armour = info["armour"]
        self.armour = info["armour"]
        self.resistances = info["damage resistances"].copy()
        self.damage_taken = False
        self.armour_break = False

        # |Animation|---------------------------------------------------------------------------------------------------
        self.sprites = False
        if "sprites" in info:
            self.sprites = info["sprites"]
        if type(self.sprites) == str:
            if Fun.SPOOKY_DAY and self.name in player_repertory:
                self.sprites = self.sprites.split(".")[0]
                self.sprites += " - Halloween.png"
            sprite = Fun.get_image(self.sprites)
            self.sprites = Fun.desheetator(sprite)
            if "Outline" in info["free var"]:
                colour = info["free var"]["Outline"]
                if "Is VIP" in info["free var"]:
                    colour = Fun.AMBER
                for count_2, d in enumerate(self.sprites):
                    for count, s in enumerate(d["Walk"]):
                        self.sprites[count_2]["Walk"][count] = Fun.get_outline(s, colour=colour)

        self.draw_aim_line = False
        self.animation_counter = {"Standing": 0,  # Should stay at 0
                                  "Walk": 0}
        self.force_draw = False
        # These are not handled by the player
        self.weapon_draw_dist, self.draw_angle, self.draw_rotated_dist = 0, 0, 0
        self.draw_targeting_range = 0

        # |Position|----------------------------------------------------------------------------------------------------
        self.pos = pos
        self.thiccness = info["thickness"]
        self.collision_box = pg.Rect(self.pos[0] - self.thiccness // 2, self.pos[1] - self.thiccness // 2,
                                     self.thiccness, self.thiccness)
        self.mouse_pos = [0, 0]
        self.angle = start_angle
        self.controller_angle = start_angle
        self.aim_angle = self.angle

        self.pathfinding_old_positions = []
        # |Movement|----------------------------------------------------------------------------------------------------
        self.standing_still = True
        self.walking = False
        self.running = False
        self.dash_allowed = True

        self.vel = [0, 0]
        self.vel_max = info["vel max"]
        self.speed = info["speed"]
        self.friction = info["friction"]
        self.direction_angle = Fun.angle_between([self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]], self.pos)

        self.dash_cooldown = 0
        self.dash_speed = 0
        self.dash_iframes = 0
        self.dash_charge_time = 0
        if "dash" in info:
            self.dash_speed = info["dash"]["speed"]
            self.dash_iframes = info["dash"]["i-frames"]
            self.dash_charge_time = info["dash"]["charge"]

        # |Inputs|------------------------------------------------------------------------------------------------------
        self.control = Fun.PseudoPlayer().control
        self.mouse_control = Fun.get_from_json("Key binds.json", "Mouse")
        self.controller_control = Fun.get_from_json("Controller binds.json", "Everything")

        self.input = Fun.get_default_inputs()
        self.input_mode = "Keyboard"
        if "Input mode" in info:
            self.input_mode = "Controller"

        # |Weapons|-----------------------------------------------------------------------------------------------------
        self.weapon = info["weapon"]    # Make it use a string to get the weapon
        if type(self.weapon) == str:
            self.weapon = Weapons.BasicWeapon(Weapons.weapon_repertory[self.weapon])

        self.no_shoot_state = 60
        self.shot_allowed = True
        self.reloading = False
        self.shooting = False

        # |Functions|---------------------------------------------------------------------------------------------------
        self.func_input = info["func input"]
        if type(self.func_input) == str:
            self.func_input = getattr(sys.modules[__name__], self.func_input)
        self.func_act = info["func act"]
        if type(self.func_act) == str:
            self.func_act = getattr(sys.modules[__name__], self.func_act)
        self.func_draw = info["func draw"]
        if type(self.func_draw) == str:
            self.func_draw = getattr(sys.modules[__name__], self.func_draw)

        self.on_death = info["on death"]
        if type(self.on_death) == str:
            self.on_death = getattr(sys.modules[__name__], self.on_death)

        # |Targeting|---------------------------------------------------------------------------------------------------
        self.ai_state = "Follow"    # For allies, Follow, Hold, Attack, Freely
        self.targeting_range = info["targeting range"]
        self.stealth_mod = 1        # 0 - 1
        if "stealth mod" in info:
            self.stealth_mod = info["stealth mod"]
        self.stealth_counter = 1    # 0 - 1
        if "stealth counter" in info:
            self.stealth_counter = info["stealth counter"]
        self.is_targeting = False  # Track if the enemy has a target
        self.is_targeted = False  # Track if the enemy has a target
        self.is_target = False
        self.targeting_angle = info["targeting angle"]
        self.wall_hack = info["wall hack"]  # This allows enemies to see you though walls
        self.target = []
        self.agro = 0
        self.did_agro_raise = 0
        self.agro_decrease_rate = 1
        self.order_builder = {
            "Current order": False,
            "Cooldown": 0,
            "Time limit": 120,
            "Allow input": True
        }

        # |Skills|------------------------------------------------------------------------------------------------------
        self.skills = []
        if "skills" in info:
            self.skills = info["skills"].copy()
        for count, s in enumerate(self.skills):
            skill_dict = s
            if type(skill_dict) == str:
                skill_dict = Skills.skill_repertory[skill_dict].copy()
            self.skills[count] = Skills.Skill(skill_dict)

        # |Misc|--------------------------------------------------------------------------------------------------------
        self.status = Fun.STATUS_EFFECT_ZERO.copy()
        self.time = 0
        self.cutscene_mode = []
        self.sound_mod = 1
        self.driving = 0
        if "driving" in info:
            self.driving = info["driving"]
        self.free_var = info["free var"].copy()

        self.bullets_shot = []
        self.upgrades = []
        # ||-

    def get_input(self, entities, level):
        self.draw_aim_line = False
        self.time += 1
        # Check for input form the Keyboard
        self.input = Fun.get_default_inputs()
        self.func_input(self, entities, level)


        # Cinematic mode
        Fun.cutscene_mode(self, entities, level)
        # self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    def act(self, entities, level):
        # Reset variables
        self.shooting = False
        self.crit = False
        self.bullets_shot = []
        self.func_act(self, entities, level)

        for upgrade in self.upgrades:
            upgrade.act(entities, level)

        agro_system(self)
        self.is_targeted = False

    def shoot_bullet(self, entities, level, guarantee_crit=False):

        # Fun.play_sound(self.weapon.gunshot_sound, "SFX", modified_volume=self.weapon.volume)
        self.shooting = True
        entities["sounds"].append(Fun.Sound(
            Fun.move_with_vel_angle(self.pos, 20, self.aim_angle),
            Fun.sounds_dict[self.weapon.gunshot_sound]["Sound"].get_length() * 60,
            (500 * self.weapon.volume + 50) * self.sound_mod,
            source=self.team, strength=2))
        self.agro += self.weapon.agro_gain
        if self.agro > 100:
            self.agro = 100
        self.did_agro_raise = 60 * 3
        # Spawn the bullets
        for b in range(Fun.bullet_x3_manager(self.weapon.bullets_per_shot, self.status["Bullet x3"])):
            Bullets.spawn_bullet(self, entities, self.weapon.bullet_type, Fun.move_with_vel_angle(self.pos, 20, self.aim_angle),
                                 self.aim_angle + random.uniform(-self.weapon.accuracy,
                                                                 self.weapon.accuracy) + random.uniform(
                                     -self.weapon.spread, self.weapon.spread), self.weapon.bullet_info)

            # Critical shots
            Fun.crit_manager(self, entities, self.weapon, guarantee_crit)
            # |Status effects management|-------------------------------------------------------------------
            Fun.bullet_status_manager(self, entities)
            self.bullets_shot.append(entities["bullets"][-1])
        sound = self.weapon.gunshot_sound
        if self.crit:
            sound = "Crit Shoot"
            # Fun.play_sound("Crit Shoot", "SFX", modified_volume=self.weapon.volume)
        Fun.play_sound(sound, "SFX", modified_volume=self.weapon.volume)
        # else:
        #     Fun.play_sound(self.weapon.gunshot_sound, "SFX", modified_volume=self.weapon.volume)

        Fun.after_shooting_manager(self, self.weapon)
        #

    def draw(self, screen, scrolling):
        self.func_draw(self, screen, scrolling)
        #

    def death(self, entities, level, scrolling_target_entities):
        self.on_death(self, entities, level)
        if (self.team != "Players" or self.team in ["Player 0", "Player 1", "Player 2", "Player 3", "Player 4"]) or self.health > 0:
            return
        for count, p in enumerate(scrolling_target_entities):
            if p == self:
                scrolling_target_entities.pop(count)
                return

    def draw_player(self, scrolling, WIN, player_direction):
        # Use this as a base for the animation function for the rest of the entities
        # Get the action (walk, dash)
        frame_to_get = 0
        action_type = "Walk"
        # Make the counters go up
        for counter in self.animation_counter:
            if action_type == counter:
                self.animation_counter[counter] += 1
            else:
                self.animation_counter[counter] = 0
        # Sliding need a special case to handle its animation
        if not self.standing_still:
            # print(player_direction)
            frame_to_get = self.animation_counter[action_type] // 7 % (
                    len(self.sprites[player_direction][action_type]) - 1) + 1

        # Draws the player
        sprite_drawn = self.sprites[player_direction][action_type][frame_to_get]
        WIN.blit(sprite_drawn, (self.pos[0] - 16 + scrolling[0], self.pos[1] - 16 + scrolling[1]))
    #


# print([p for p in dir(Entity)])



def draw_aim_line(self, entities):
    if not self.draw_aim_line:
        return
        # Get the max angle
        #
        #         "Startup lag": 0,
        #         "Startup time": 120
    draw_pos = Fun.move_with_vel_angle(self.pos, 20, self.aim_angle)
    angle = self.aim_angle
    drawing_pos = Fun.move_with_vel_angle(draw_pos, 20, angle)
    length = self.weapon.range + 20

    # Draw the lines
    mod = self.free_var["Startup lag"]/self.free_var["Startup time"]

    colour_index = [1]
    if "aim line colour" in self.free_var:
        colour_index = self.free_var["aim line colour"]
    bg_colour = [0, 0, 0]
    fg_colour = [0, 0, 0]
    for i in colour_index:
        bg_colour[i] = 125
    for i in colour_index:
        fg_colour[i] = 255 * mod

    entities["background particles"].append(Fun.LineParticle(drawing_pos, bg_colour, 1, length, angle, 1, 0))

    entities["background particles"].append(Fun.LineParticle(
        drawing_pos, fg_colour, 1, length * mod, angle, 3,
        0))


def draw_weapon(self, WIN, scrolling):
    draw_pos = [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]]
    angle_to_add = 0
    if self.reloading:
        angle_to_add = (360 / self.weapon.reload_time) * self.no_shoot_state

    # self.draw_angle
    drawing_pos = Fun.move_with_vel_angle(draw_pos, 6 + self.weapon_draw_dist, self.aim_angle)
    drawing_pos = Fun.move_with_vel_angle(drawing_pos, self.draw_rotated_dist, self.aim_angle + self.draw_angle)
    origin = [0, self.weapon.sprite.get_height() // 2]

    Fun.blitRotate(WIN, pg.transform.flip(self.weapon.sprite, True, -90 < self.aim_angle < 90),
                   drawing_pos, origin, 180 - self.aim_angle + angle_to_add + self.draw_angle)


# |Player inputs|-------------------------------------------------------------------------------------------------------
def player_act(self, entities, level):
    # |Aim system|--------------------------------------------------------------------------------------------------
    Fun.aim_system(self, self.weapon)
    # |Movement Input|----------------------------------------------------------------------------------------------
    Fun.movement_player(self, entities)
    # Fun.movement_entity(self)

    # |GunPlay|-----------------------------------------------------------------------------------------------------
    entities["UI particles"].append(Fun.AimPoint(self.mouse_pos))
    # if self.weapon.ammo == 0 and self.weapon.ammo_cost > 0:
    #     entities["UI particles"].append(
    #         Fun.FloatingTextType2([self.mouse_pos[0], self.mouse_pos[1] - 12],
    #                               18, Fun.write_textline("Input type Reload"), Fun.UI_COLOUR_TUTORIAL, 1)
    #     )
    self.weapon.passive(self, entities, level)
    if self.no_shoot_state == 0:
        # Reset variables
        self.reloading = False

        # Alternative fire
        # print(self.input)
        if self.input["Alt fire"]:
            self.weapon.alt_fire(self, entities, level)

        # |Main fire|-----------------------------------------------------------------------------------------------
        if self.input["Shoot"]:
            if self.weapon.ammo != 0 and self.shot_allowed:
                # |Main fire|-------------------------------------------------------------------------------------------
                self.shoot_bullet(entities, level)
                # tell if the trigger was pressed
                if not self.weapon.full_auto:
                    self.shot_allowed = False
            # if the trigger is not pressed and the weapon is not a full auto, allow to shoot for the next trigger press
            elif self.weapon.ammo == 0 and self.shot_allowed:
                Fun.play_sound(self.weapon.jamming_sound, "SFX")
                self.shot_allowed = False
        else:
            self.shot_allowed = True

        # |Reload|--------------------------------------------------------------------------------------------------
        if self.input["Reload"] and self.weapon.ammo_pool > 0:
            self.no_shoot_state, self.reloading = self.weapon.reload()

    else:
        self.no_shoot_state -= 1

    # |Skills|------------------------------------------------------------------------------------------------------
    Skills.skills_manager(self, entities, level)

    # |Status effects|----------------------------------------------------------------------------------------------
    # ha ha, Fun go brr
    Fun.status_manager(self, entities)

    # |Movement Output|---------------------------------------------------------------------------------------------
    # Make the player move
    Fun.movement_output(self, level)
    if self.draw_aim_line or self.weapon.laser_sight:
        entities["background particles"].append(Fun.LineParticle(
            Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), Fun.BLUE, 1, self.weapon.range-20, self.aim_angle, 2, 0))
    # Give orders
    if self.order_builder["Cooldown"] <= 0:
        if self.order_builder["Current order"]:
            self.order_builder["Time limit"] -= 1
            # Write
            mod = 10
            pos = [self.pos[0] + 16, self.pos[1] - 48]
            entities["particles"].append(Fun.FloatingTextType3(pos.copy(), 18, self.order_builder["Current order"], Fun.AMBER, 1))
            pos[1] += mod
            for x in [
                f"{Fun.write_control(self, "Order Hold")}All Teammate",
                f"{Fun.write_control(self, "Order Follow")}Teammate 1",
                f"{Fun.write_control(self, "Order Attack")}Teammate 2",
                f"{Fun.write_control(self, "Order Act Free")}Teammate 3"]:
                pos[1] += mod
                entities["particles"].append(Fun.FloatingTextType3(pos.copy(), 18, x, Fun.AMBER, 1))
            pos[1] += mod
            entities["particles"].append(Fun.GrowingSquare([pos[0], pos[1], 120, 8], Fun.UI_COLOUR_NEW_BACKDROP, [0, 0], 1))
            entities["particles"].append(Fun.GrowingSquare([pos[0], pos[1], self.order_builder["Time limit"]//3, 8], Fun.AMBER_LIGHT, [0, 0], 1))

            # Choose who to give the order to
            if self.order_builder["Allow input"]:
                if self.input["Order Hold"]:
                    give_order(self, entities, [1, 2, 3])
                if self.input["Order Follow"]:
                    give_order(self, entities, [1])
                if self.input["Order Attack"]:
                    give_order(self, entities, [2])
                if self.input["Order Act Free"]:
                    give_order(self, entities, [3])
            elif not (self.input["Order Hold"] or self.input["Order Follow"] or self.input["Order Attack"] or self.input["Order Act Free"]):
                self.order_builder["Allow input"] = True

            # Reset if time out
            if self.order_builder["Time limit"] < 0:
                self.order_builder["Current order"] = False
                self.order_builder["Cooldown"] = 120
        else:
            # Choose the order
            opt = False
            if self.input["Order Hold"]:
                opt = True
                self.order_builder["Current order"] = "Hold"
            if self.input["Order Follow"]:
                opt = True
                self.order_builder["Current order"] = "Follow"
            if self.input["Order Attack"]:
                opt = True
                self.order_builder["Current order"] = "Attack"
            if self.input["Order Act Free"]:
                opt = True
                self.order_builder["Current order"] = "Freely"

            # Add cooldown
            if opt:

                self.order_builder["Allow input"] = False
                self.order_builder["Time limit"] =  120 * 3

    else:
        self.order_builder["Cooldown"] -= 1

    if self.armour_break:
        # Need a sound effect
        self.armour_break = False
        number_of_particle = 18
        for particles_to_add in range(360 // number_of_particle):
            entities["background particles"].append(Fun.RandomParticle2(
                [self.pos[0], self.pos[1]], Fun.GREEN, 2 * random.random(), random.randint(15, 45),
                                                        particles_to_add * number_of_particle,
                size=Fun.get_random_element_from_list([3, 4, 6])))


def fortress_act(self, entities, level):
    vehicle_escort(self, level)
    angle = self.free_var["Move angle"] + 226 - 180
    pos = [self.pos[0], self.pos[1] - 16]
    pos = Fun.move_with_vel_angle(pos, 22.6274, angle)
    pos = Fun.move_with_vel_angle(pos, 20, self.aim_angle)
    # |Movement Input|----------------------------------------------------------------------------------------------
    self.running = False
    self.walking = False

    max_vel = self.vel_max

    # Handle double speed and slowness status
    if self.status["Slowness"]:
        max_vel *= 0.5
    if self.status["Double speed"]:
        max_vel *= 2

    # Checks for which direction the player must move
    # Rework it so that you are not faster when walking in diagonal, this should be fixed now
    if self.dash_cooldown <= 0:
        allow_correction = False
        speed = 0
        if self.input["Up"]:
            speed = 1
            allow_correction = True
        if self.input["Down"]:
            speed = -1
            allow_correction = True
        if self.input["Left"]:
            self.free_var["Move angle"] -= 3
        if self.input["Right"]:
            self.free_var["Move angle"] += 3
        self.vel = Fun.move_with_vel_angle(self.vel, self.speed * speed, self.free_var["Move angle"])

        if not Fun.check_point_in_circle(max_vel, 0, 0, self.vel[0], self.vel[1]) and allow_correction:
            self.vel = Fun.move_with_vel_angle([0, 0], max_vel * speed, self.free_var["Move angle"])
        self.walking = allow_correction

        if self.free_var["Move angle"] > 180:
            self.free_var["Move angle"] = -180 + (self.free_var["Move angle"] - 180)
        if self.free_var["Move angle"] < -180:
            self.free_var["Move angle"] = 180 - (self.free_var["Move angle"] + 180)

    self.standing_still = False
    if self.vel == [0, 0]:
        self.standing_still = True
    elif self.cutscene_mode:
        # This makes entities use their walking animation during cutscenes
        self.walking = True

    # Dash mechanic
    if self.dash_cooldown <= 0 and not self.standing_still and self.input["Dash"]:
        # Handle dash here
        Fun.play_sound("Player dash", modified_volume=0.25)
        dash_angle = self.free_var["Move angle"]
        self.dash_cooldown = self.dash_charge_time
        if self.status["Dash recovery up"] > 0:
            self.dash_cooldown //= 2
        self.vel = Fun.move_with_vel_angle(self.vel, self.dash_speed / self.friction * speed, dash_angle)
        for x in range(4):
            angle = dash_angle - 15 - 3.25 * 2 + x * 7.5 * 2
            entities["particles"].append(
                Fun.RandomParticle2(
                    Fun.move_with_vel_angle([self.pos[0], self.pos[1]], -4, angle),
                    Fun.WHITE, 1.5 + random.uniform(0, 2), 24, angle))

        if self.status["No damage"] < self.dash_iframes:
            self.status["No damage"] += self.dash_iframes
    self.dash_cooldown -= 1

    # |GunPlay|-----------------------------------------------------------------------------------------------------
    angle = self.aim_angle
    drawing_pos = pos
    length = self.weapon.range + 20

    # Draw the lines
    entities["background particles"].append(Fun.LineParticle(drawing_pos, Fun.RED, 1, length, angle, 1, 0))

    entities["UI particles"].append(Fun.AimPoint(self.mouse_pos))
    self.weapon.passive(self, entities, level)
    if self.no_shoot_state == 0:
        # Reset variables
        self.reloading = False

        if self.input["Alt fire"]:
            self.weapon.alt_fire(self, entities, level)

        # |Main fire|-----------------------------------------------------------------------------------------------
        if self.input["Shoot"]:
            if self.weapon.ammo != 0 and self.shot_allowed:
                # |Main fire|-------------------------------------------------------------------------------------------
                self.shoot_bullet(entities, level)

                # tell if the trigger was pressed
                if not self.weapon.full_auto:
                    self.shot_allowed = False
            # if the trigger is not pressed and the weapon is not a full auto, allow to shoot for the next trigger press
            elif self.weapon.ammo == 0 and self.shot_allowed:
                Fun.play_sound(self.weapon.jamming_sound, "SFX")
                self.shot_allowed = False
        else:
            self.shot_allowed = True

        # |Reload|--------------------------------------------------------------------------------------------------
        if self.input["Reload"] and self.weapon.ammo_pool > 0:
            self.no_shoot_state, self.reloading = self.weapon.reload()
    else:
        self.no_shoot_state -= 1

    Fun.aim_system(self, self.weapon)

    # |Skills|------------------------------------------------------------------------------------------------------
    Skills.skills_manager(self, entities, level)

    # |Status effects|----------------------------------------------------------------------------------------------
    # ha ha, Fun go brr
    Fun.status_manager(self, entities)

    # |Movement Output|---------------------------------------------------------------------------------------------
    # Make the player move
    Fun.movement_output(self, level)
    for e in entities["entities"]:
        if e == self: continue
        if self.collision_box.colliderect(e.collision_box):
            e.vel = Fun.move_with_vel_angle(e.vel, 2, Fun.angle_between(e.collision_box.center, self.pos))
            if e.team != self.team:
                Fun.damage_calculation(e, round(abs(self.vel[0]) + abs(self.vel[1])) * 5, "Melee", death_message="Ran over")
            pass
    if self.draw_aim_line or self.weapon.laser_sight:
        entities["background particles"].append(Fun.LineParticle(
            Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), Fun.BLUE, 1, self.weapon.range-20, self.aim_angle, 2, 0))
    # Give orders
    if self.order_builder["Cooldown"] <= 0:
        if self.order_builder["Current order"]:
            self.order_builder["Time limit"] -= 1
            # Write
            mod = 10
            pos = [self.pos[0] + 16, self.pos[1] - 48]
            entities["particles"].append(Fun.FloatingTextType3(pos.copy(), 18, self.order_builder["Current order"], Fun.AMBER, 1))
            pos[1] += mod
            for x in [
                f"{Fun.write_control(self, "Order Hold")}All Teammate",
                f"{Fun.write_control(self, "Order Follow")}Teammate 1",
                f"{Fun.write_control(self, "Order Attack")}Teammate 2",
                f"{Fun.write_control(self, "Order Act Free")}Teammate 3"]:
                pos[1] += mod
                entities["particles"].append(Fun.FloatingTextType3(pos.copy(), 18, x, Fun.AMBER, 1))
            pos[1] += mod
            entities["particles"].append(Fun.GrowingSquare([pos[0], pos[1], 120, 8], Fun.UI_COLOUR_NEW_BACKDROP, [0, 0], 1))
            entities["particles"].append(Fun.GrowingSquare([pos[0], pos[1], self.order_builder["Time limit"]//3, 8], Fun.AMBER_LIGHT, [0, 0], 1))

            # Choose who to give the order to
            if self.order_builder["Allow input"]:
                if self.input["Order Hold"]:
                    give_order(self, entities, [1, 2, 3])
                if self.input["Order Follow"]:
                    give_order(self, entities, [1])
                if self.input["Order Attack"]:
                    give_order(self, entities, [2])
                if self.input["Order Act Free"]:
                    give_order(self, entities, [3])
            elif not (self.input["Order Hold"] or self.input["Order Follow"] or self.input["Order Attack"] or self.input["Order Act Free"]):
                self.order_builder["Allow input"] = True

            # Reset if time out
            if self.order_builder["Time limit"] < 0:
                self.order_builder["Current order"] = False
                self.order_builder["Cooldown"] = 240
        else:
            # Choose the order
            opt = False
            if self.input["Order Hold"]:
                opt = True
                self.order_builder["Current order"] = "Hold"
            if self.input["Order Follow"]:
                opt = True
                self.order_builder["Current order"] = "Follow"
            if self.input["Order Attack"]:
                opt = True
                self.order_builder["Current order"] = "Attack"
            if self.input["Order Act Free"]:
                opt = True
                self.order_builder["Current order"] = "Freely"

            # Add cooldown
            if opt:

                self.order_builder["Allow input"] = False
                self.order_builder["Time limit"] =  120 * 3

    else:
        self.order_builder["Cooldown"] -= 1

    if self.armour_break:
        # Need a sound effect
        self.armour_break = False
        number_of_particle = 18
        for particles_to_add in range(360 // number_of_particle):
            entities["background particles"].append(Fun.RandomParticle2(
                [self.pos[0], self.pos[1]], Fun.GREEN, 2 * random.random(), random.randint(15, 45),
                                                        particles_to_add * number_of_particle,
                size=Fun.get_random_element_from_list([3, 4, 6])))


def buggy_act(self, entities, level):
    vehicle_escort(self, level)
    angle = self.free_var["Move angle"] + 226 - 180
    pos = [self.pos[0], self.pos[1] - 16]
    pos = Fun.move_with_vel_angle(pos, 22.6274, angle)
    pos = Fun.move_with_vel_angle(pos, 20, self.aim_angle)
    # |Movement Input|----------------------------------------------------------------------------------------------
    self.running = False
    self.walking = False

    max_vel = self.vel_max

    # Handle double speed and slowness status
    if self.status["Slowness"]:
        max_vel *= 0.5
    if self.status["Double speed"]:
        max_vel *= 2

    # Checks for which direction the player must move
    # Rework it so that you are not faster when walking in diagonal, this should be fixed now
    if self.dash_cooldown <= 0:
        allow_correction = False
        speed = 0
        if self.input["Up"]:
            speed = 1
            allow_correction = True
        if self.input["Down"]:
            speed = -1
            allow_correction = True

        mod = 0.7
        angle_type = "Move angle"
        if self.skills[0].recharge == 0:
            angle_type = "Target Move angle"
            mod = 2
        self.free_var["Move vel"] = abs(self.vel[0]) + abs(self.vel[1])

        # Fun.move_angle_toward_target_angle(real_angle, target_angle, rate)
        turn_vel = self.free_var["Move vel"] * 0.8
        if self.free_var["Move vel"] > 0 and turn_vel < 1:
            turn_vel = 1
        if turn_vel > 4:
            turn_vel = 4
        if self.input["Left"]:
            self.free_var["Target Move angle"] -= turn_vel
        if self.input["Right"]:
            self.free_var["Target Move angle"] += turn_vel
        self.free_var["Target Move angle"] = Fun.angle_value_limiter(self.free_var["Target Move angle"])
        self.free_var["Move angle"] = Fun.move_angle_toward_target_angle(self.free_var["Move angle"], self.free_var["Target Move angle"], turn_vel * mod)

        self.vel = Fun.move_with_vel_angle(self.vel, self.speed * speed, self.free_var[angle_type])
        if not Fun.check_point_in_circle(max_vel, 0, 0, self.vel[0], self.vel[1]) and allow_correction:
            self.vel = Fun.move_with_vel_angle([0, 0], max_vel * speed, self.free_var[angle_type])
        self.walking = allow_correction
    #
    self.standing_still = False
    if self.vel == [0, 0]:
        self.standing_still = True
    elif self.cutscene_mode:
        # This makes entities use their walking animation during cutscenes
        self.walking = True

    # Dash mechanic
    if self.dash_cooldown <= 0 and not self.standing_still and self.input["Dash"]:
        # Handle dash here
        Fun.play_sound("Player dash", modified_volume=0.25)
        dash_angle = self.free_var["Move angle"]
        self.dash_cooldown = self.dash_charge_time
        if self.status["Dash recovery up"] > 0:
            self.dash_cooldown //= 2
        self.vel = Fun.move_with_vel_angle(self.vel, self.dash_speed / self.friction * speed, dash_angle)
        for x in range(4):
            angle = dash_angle - 15 - 3.25 * 2 + x * 7.5 * 2
            entities["particles"].append(
                Fun.RandomParticle2(
                    Fun.move_with_vel_angle([self.pos[0], self.pos[1]], -4, angle),
                    Fun.WHITE, 1.5 + random.uniform(0, 2), 24, angle))

        if self.status["No damage"] < self.dash_iframes:
            self.status["No damage"] += self.dash_iframes
    self.dash_cooldown -= 1

    # |GunPlay|-----------------------------------------------------------------------------------------------------
    length = self.weapon.range + 20

    # Draw the lines
    entities["background particles"].append(Fun.LineParticle(self.pos, Fun.RED, 1, length, self.free_var["Move angle"], 1, 0))

    entities["UI particles"].append(Fun.AimPoint(self.mouse_pos))
    self.weapon.passive(self, entities, level)
    if self.no_shoot_state == 0:
        # Reset variables
        self.reloading = False

        if self.input["Alt fire"]:
            self.weapon.alt_fire(self, entities, level)

        # |Main fire|-----------------------------------------------------------------------------------------------
        if self.input["Shoot"]:
            if self.weapon.ammo != 0 and self.shot_allowed:
                # |Main fire|-------------------------------------------------------------------------------------------
                self.shoot_bullet(entities, level)

                # tell if the trigger was pressed
                if not self.weapon.full_auto:
                    self.shot_allowed = False
            # if the trigger is not pressed and the weapon is not a full auto, allow to shoot for the next trigger press
            elif self.weapon.ammo == 0 and self.shot_allowed:
                Fun.play_sound(self.weapon.jamming_sound, "SFX")
                self.shot_allowed = False
        else:
            self.shot_allowed = True

        # |Reload|--------------------------------------------------------------------------------------------------
        if self.input["Reload"] and self.weapon.ammo_pool > 0:
            self.no_shoot_state, self.reloading = self.weapon.reload()
    else:
        self.no_shoot_state -= 1

    Fun.aim_system(self, self.weapon)

    # |Skills|------------------------------------------------------------------------------------------------------
    Skills.skills_manager(self, entities, level)

    # |Status effects|----------------------------------------------------------------------------------------------
    # ha ha, Fun go brr
    Fun.status_manager(self, entities)

    # |Movement Output|---------------------------------------------------------------------------------------------
    # Make the player move
    Fun.movement_output(self, level)
    for e in entities["entities"]:
        if e == self: continue
        if self.collision_box.colliderect(e.collision_box):
            e.vel = Fun.move_with_vel_angle(e.vel, 2, Fun.angle_between(e.collision_box.center, self.pos))
            if e.team != self.team:
                Fun.damage_calculation(e, round(abs(self.vel[0]) + abs(self.vel[1])) * 5, "Melee", death_message="Ran over")
            pass
    if self.draw_aim_line or self.weapon.laser_sight:
        pos = Fun.move_with_vel_angle(self.pos, -24, self.free_var["Move angle"])
        entities["background particles"].append(Fun.LineParticle(
            [pos[0], pos[1]-14], Fun.BLUE, 1, self.weapon.range-20,
            self.aim_angle, 2, 0))
    # Give orders
    if self.order_builder["Cooldown"] <= 0:
        if self.order_builder["Current order"]:
            self.order_builder["Time limit"] -= 1
            # Write
            mod = 10
            pos = [self.pos[0] + 16, self.pos[1] - 48]
            entities["particles"].append(Fun.FloatingTextType3(pos.copy(), 18, self.order_builder["Current order"], Fun.AMBER, 1))
            pos[1] += mod
            for x in [
                f"{Fun.write_control(self, "Order Hold")}All Teammate",
                f"{Fun.write_control(self, "Order Follow")}Teammate 1",
                f"{Fun.write_control(self, "Order Attack")}Teammate 2",
                f"{Fun.write_control(self, "Order Act Free")}Teammate 3"]:
                pos[1] += mod
                entities["particles"].append(Fun.FloatingTextType3(pos.copy(), 18, x, Fun.AMBER, 1))
            pos[1] += mod
            entities["particles"].append(Fun.GrowingSquare([pos[0], pos[1], 120, 8], Fun.UI_COLOUR_NEW_BACKDROP, [0, 0], 1))
            entities["particles"].append(Fun.GrowingSquare([pos[0], pos[1], self.order_builder["Time limit"]//3, 8], Fun.AMBER_LIGHT, [0, 0], 1))

            # Choose who to give the order to
            if self.order_builder["Allow input"]:
                if self.input["Order Hold"]:
                    give_order(self, entities, [1, 2, 3])
                if self.input["Order Follow"]:
                    give_order(self, entities, [1])
                if self.input["Order Attack"]:
                    give_order(self, entities, [2])
                if self.input["Order Act Free"]:
                    give_order(self, entities, [3])
            elif not (self.input["Order Hold"] or self.input["Order Follow"] or self.input["Order Attack"] or self.input["Order Act Free"]):
                self.order_builder["Allow input"] = True

            # Reset if time out
            if self.order_builder["Time limit"] < 0:
                self.order_builder["Current order"] = False
                self.order_builder["Cooldown"] = 240
        else:
            # Choose the order
            opt = False
            if self.input["Order Hold"]:
                opt = True
                self.order_builder["Current order"] = "Hold"
            if self.input["Order Follow"]:
                opt = True
                self.order_builder["Current order"] = "Follow"
            if self.input["Order Attack"]:
                opt = True
                self.order_builder["Current order"] = "Attack"
            if self.input["Order Act Free"]:
                opt = True
                self.order_builder["Current order"] = "Freely"

            # Add cooldown
            if opt:

                self.order_builder["Allow input"] = False
                self.order_builder["Time limit"] =  120 * 3

    else:
        self.order_builder["Cooldown"] -= 1

    if self.armour_break:
        # Need a sound effect
        self.armour_break = False
        number_of_particle = 18
        for particles_to_add in range(360 // number_of_particle):
            entities["background particles"].append(Fun.RandomParticle2(
                [self.pos[0], self.pos[1]], Fun.GREEN, 2 * random.random(), random.randint(15, 45),
                                                        particles_to_add * number_of_particle,
                size=Fun.get_random_element_from_list([3, 4, 6])))


# Keyboard input
def player_input_keyboard(self, entities, level):
    Fun.keyboard_mouse_input(self, pg.key.get_pressed(), pg.mouse.get_pressed(3))

    width, height = pg.display.get_surface().get_size()
    slide_width, slide_height = Fun.FRAME_MAX_SIZE  # 1.4
    if width != slide_width or height != slide_height:
        if width > height * 1.4:
            slide_width = slide_width * height / slide_height
            slide_height = height
        elif width < height:
            slide_height = slide_height * width / slide_width
            slide_width = width
        if width < height * 1.4:
            slide_width = slide_width * height / slide_height
            slide_height = height
        elif width > height:
            slide_height = slide_height * width / slide_width
            slide_width = width
    if slide_width > width or slide_height > height:
        if width > height * 1.4:
            slide_width = slide_width * height / slide_height
            slide_height = height
        elif width < height * 1.4:
            slide_height = slide_height * width / slide_width
            slide_width = width
    mouse_pos = pg.mouse.get_pos()
    render_rect = (width // 2 - slide_width // 2, height // 2 - slide_height // 2, slide_width, slide_height)
    self.mouse_pos = [(mouse_pos[0] - render_rect[0]) * (Fun.FRAME_MAX_SIZE[0] / slide_width) - entities["scrolling"][0],
                      (mouse_pos[1] - render_rect[1]) * (Fun.FRAME_MAX_SIZE[1] / slide_height) - entities["scrolling"][1]]
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)
    Fun.stunned_manager(self)


# Controller input
def player_input_controller_1(self, entities, level):
    Fun.controller_input(self, gamepad_index=0)
    Fun.stunned_manager(self)


def player_input_controller_2(self, entities, level):
    Fun.controller_input(self, gamepad_index=1)
    Fun.stunned_manager(self)


def player_input_controller_3(self, entities, level):
    Fun.controller_input(self, gamepad_index=2)
    Fun.stunned_manager(self)


def player_input_controller_4(self, entities, level):
    Fun.controller_input(self, gamepad_index=3)
    Fun.stunned_manager(self)


def give_order(self, entities, targets):
    self.order_builder["Cooldown"] = 240
    allies_found = 0
    for x in entities["entities"]:
        # Make sure to not give the order to an enemy
        if x.team != self.team:
            continue
        # or the player 1
        if x == self:
            continue
        allies_found += 1
        # Check if the ally is the intended target
        if allies_found in targets:
            x.ai_state = self.order_builder["Current order"]
            # Special case for follow
            if self.order_builder["Current order"] == "Follow":
                x.free_var["Ally waypoint"] = self
            # Special case for hold
            if self.order_builder["Current order"] == "Hold":
                x.free_var["Ally waypoint"] = self.mouse_pos.copy()
    self.order_builder["Current order"] = False


# |Pathfinding|---------------------------------------------------------------------------------------------------------
def universal_pathfinding(self, level, pos):
    if not Fun.wall_between(self.pos, pos, level):
        return False
    # Use the pathfinding function
    connections, points = level['pathfinding']['connections'], level['pathfinding']['points']

    # Get current location
    current_location = '0'
    control_dist = Fun.BIG_INT
    for p in points:
        test_dist = Fun.distance_between(points[p], self.pos)
        if test_dist < control_dist:
            current_location = p
            control_dist = test_dist

    # Get the target destination
    end_point = '0'
    control_dist = Fun.BIG_INT
    for p in points:
        test_dist = Fun.distance_between(points[p], pos)
        if test_dist < control_dist:
            end_point = p
            control_dist = test_dist
    path = Fun.entity_path_making(self, current_location, end_point, connections, points)
    if not path:
        return False
    point = points[path[0]]
    return point


def pathfinding(self, level):
    if not Fun.wall_between(self.pos, self.target.pos, level):
        return False
    # 'pathfinding': None, # {
    #             # 'points': {},  # "<id>": [<x>, <y>]
    #             # 'connections': {}  # "<id>": [<id of connected points>]
    #         # }
    # Use the pathfinding function
    connections = level['pathfinding']['connections']
    points = level['pathfinding']['points']

    # Get current location
    current_location = '0'
    control_dist = Fun.BIG_INT
    for p in points:
        test_dist = Fun.distance_between(points[p], self.pos)
        if test_dist < control_dist:
            current_location = p
            control_dist = test_dist

    # Get the target destination
    end_point = '0'
    control_dist = Fun.BIG_INT
    for p in points:
        if p == current_location:
            continue
        test_dist = Fun.distance_between(points[p], self.target.pos)
        if test_dist < control_dist:
            end_point = p
            control_dist = test_dist

    return points[Fun.entity_path_making(self, current_location, end_point, connections, points, [])[0]]


# |General use|---------------------------------------------------------------------------------------------------------
def start_up_lag_handler(self, target_time, key="Startup lag"):
    # This little thing make it way easier to have startup lag
    if self.free_var[key] >= target_time:
        self.free_var[key] = 0
        return True
    self.free_var[key] += 1
    return False


def entity_dodge_bullets(self, entities, look_range, bullets_to_dodge=(Bullets.Bullet, Bullets.Fire, Bullets.Missile, Bullets.Artillery)):
    bullet_to_dodge = Fun.find_closest_bullet_types_in_circle(self, entities, look_range, bullets_to_dodge)
    if bullet_to_dodge:
        # dodge_pos = Fun.move_with_vel_angle(self.pos, bullet_to_dodge.radius, bullet_to_dodge.angle  - 75)
        dodge_pos = bullet_to_dodge.pos

        self.input["Right"] = self.pos[0] > dodge_pos[0]
        self.input["Left"] = self.pos[0] < dodge_pos[0]
        self.input["Down"] = self.pos[1] > dodge_pos[1]
        self.input["Up"] = self.pos[1] < dodge_pos[1]


# Component
def entity_get_aim_move_target(self, target):
    aim_target = self.target.pos.copy()
    self.angle = Fun.angle_between(aim_target, self.pos)
    return aim_target, target.copy(), Fun.distance_between(target, self.pos)


def entity_maintain_weapon_range(self, og_dist, move_target, get_closer, get_away=64):
    if og_dist > get_closer:
        self.input["Right"] = self.pos[0] < move_target[0]
        self.input["Left"] = self.pos[0] > move_target[0]
        self.input["Down"] = self.pos[1] < move_target[1]
        self.input["Up"] = self.pos[1] > move_target[1]

    if og_dist < get_away:
        self.input["Right"] = self.pos[0] > move_target[0]
        self.input["Left"] = self.pos[0] < move_target[0]
        self.input["Down"] = self.pos[1] > move_target[1]
        self.input["Up"] = self.pos[1] < move_target[1]


def entity_shoot_no_startup_lag(self, og_dist, engage_range):
    self.input["Shoot"] = self.weapon.ammo > 0 and og_dist < engage_range


def entity_shoot_with_startup_lag(self, og_dist, engage_range):
    if self.weapon.ammo > 0 and og_dist < engage_range and self.free_var['Startup lag'] == 0 and self.status["Stunned"] == 0:
        self.free_var['Startup lag'] += 1


def entity_shoot_startup_handler(self):
    if self.free_var['Startup lag'] > 0:
        self.draw_aim_line = True
        self.input["Shoot"] = start_up_lag_handler(self, self.free_var["Startup time"])
        if not self.target:
            self.free_var['Startup lag'] = 0


def entity_shoot_melee(self, og_dist, engage_range):
    pass


def entity_spread_apart(self, entities, spread_dist=32):
    for e in entities["entities"]:
        if 0 < Fun.distance_between(e.pos, self.pos) < spread_dist:
            self.input["Right"] = self.pos[0] > e.pos[0]
            self.input["Left"] = self.pos[0] < e.pos[0]
            self.input["Down"] = self.pos[1] > e.pos[1]
            self.input["Up"] = self.pos[1] < e.pos[1]
            break


def entity_escort_ally(self, entities, level, escort_list=("VIP", "Shock"), escort_dist=48, look_dist=512):
    for e in entities["entities"]:
        if e.name not in escort_list:
            continue
        if Fun.wall_between(e.pos, self.pos, level):
            continue
        if look_dist > Fun.distance_between(e.pos, self.pos) > escort_dist:
            self.input["Right"] = self.pos[0] < e.pos[0]
            self.input["Left"] = self.pos[0] > e.pos[0]
            self.input["Down"] = self.pos[1] < e.pos[1]
            self.input["Up"] = self.pos[1] > e.pos[1]
        return


def entity_dash_when_targeted(self, no_shoot_threshold=0, threshold=0.3):
    if self != self.target.target:
        return
    self.input["Dash"] = self.target.no_shoot_state <= no_shoot_threshold and random.random() < threshold


def entity_move_toward_point(self, move_target, dist):
    if dist < Fun.distance_between(self.pos, move_target):
        self.input["Right"] = self.pos[0] < move_target[0]
        self.input["Left"] = self.pos[0] > move_target[0]
        self.input["Down"] = self.pos[1] < move_target[1]
        self.input["Up"] = self.pos[1] > move_target[1]


def entity_get_enemy_count(self, entities, goal=10, dist=256, entity_type="entities"):
    enemy_count = 0
    for e in entities[entity_type]:
        if e.team == self.team:
            continue
        if Fun.distance_between(e.pos, self.pos) < dist:
            enemy_count += 1
            if enemy_count > goal:
                break
    return enemy_count > goal


def entity_get_ally_count(self, entities, goal=10, dist=256, entity_type="entities"):
    enemy_count = 0
    for e in entities[entity_type]:
        if e.team != self.team:
            continue
        if Fun.distance_between(e.pos, self.pos) < dist:
            enemy_count += 1
            if enemy_count > goal:
                break
    return enemy_count > goal


def entity_find_main_group(self, entities, dist=128):
    allies = []
    for count, e in enumerate(entities["entities"]):
        if count > 3: break
        if e.team != self.team: continue
        allies.append(e)

    main_group = self.pos.copy()
    control_num = 0
    for a in allies:
        if not a.is_player: continue
        temp = 0
        for aa in allies:
            if Fun.distance_between(a.pos, aa.pos) < dist:
                temp += 1
        if control_num < temp:
            main_group = a.pos.copy()

    return main_group


def entity_find_teammate(self, entities, target="Sovereign"):
    for count, e in enumerate(entities["entities"]):
        if count > 3: break
        if e.team != self.team: continue
        if e.name != target: continue
        return e.pos.copy()
    return False


def fortress_move_toward_point(self, move_target, dist):
    if dist < Fun.distance_between(self.pos, move_target):
        angle = Fun.angle_between(move_target, self.pos)
        self.input["Right"] = self.free_var["Move angle"] < angle
        self.input["Left"] = self.free_var["Move angle"] > angle

        if not -(180 - 4) + angle < self.free_var["Move angle"] < 180 - 4 + angle:
            self.input["Right"] = self.free_var["Move angle"] > angle
            self.input["Left"] = self.free_var["Move angle"] < angle

        self.input["Down"] = False
        mod = [5, 6, 7, 8, 10][self.driving]
        self.input["Up"] = angle - mod < self.free_var["Move angle"] < angle + mod


def fortress_move_away_point(self, move_target, dist):
    if dist > Fun.distance_between(self.pos, move_target):
        angle = Fun.angle_between(move_target, self.pos)
        self.input["Right"] = self.free_var["Move angle"] < angle
        self.input["Left"] = self.free_var["Move angle"] > angle

        if not -(180 - 4) + angle < self.free_var["Move angle"] < 180 - 4 + angle:
            self.input["Right"] = self.free_var["Move angle"] > angle
            self.input["Left"] = self.free_var["Move angle"] < angle

        self.input["Down"] = angle - 12 < self.free_var["Move angle"] < angle + 12
        self.input["Up"] = False
        # self.input["Up"] = angle - mod < self.free_var["Move angle"] < angle + mod


def buggy_move_toward_point(self, move_target, dist):
    if dist < Fun.distance_between(self.pos, move_target):
        angle = Fun.angle_between(move_target, self.pos)
        self.input["Right"] = self.free_var["Move angle"] < angle
        self.input["Left"] = self.free_var["Move angle"] > angle

        if not -(180 - 4) + angle < self.free_var["Move angle"] < 180 - 4 + angle:
            self.input["Right"] = self.free_var["Move angle"] > angle
            self.input["Left"] = self.free_var["Move angle"] < angle

        self.input["Down"] = False
        mod = [8, 10, 12, 14, 16][self.driving]
        self.input["Up"] = angle - mod < self.free_var["Move angle"] < angle + mod or (self.input["Right"] or self.input["Left"]) and self.time % 3 != 0


def buggy_move_away_point(self, move_target, dist):
    if dist > Fun.distance_between(self.pos, move_target):
        angle = Fun.angle_between(move_target, self.pos)
        self.input["Left"] = self.free_var["Move angle"] < angle
        self.input["Right"] = self.free_var["Move angle"] > angle

        if not -(180 - 4) + angle < self.free_var["Move angle"] < 180 - 4 + angle:
            self.input["Left"] = self.free_var["Move angle"] > angle
            self.input["Right"] = self.free_var["Move angle"] < angle

        self.input["Up"] = False
        mod = [8, 10, 12, 14, 16][self.driving]
        self.input["Down"] = angle - mod < self.free_var["Move angle"] < angle + mod or (self.input["Right"] or self.input["Left"]) and self.time % 3 != 0


# |Targeting|-----------------------------------------------------------------------------------------------------------
def entity_target_detection(self, entities, level):
    # Used by the enemy AI able to find targets
    # Might make them capable of patrolling

    if self.time % 240 == 0 or not self.target:
        self.is_target = False
        self.target = False
        target_check = self.targeting_range
        # I might have to remake the whole targeting system
        control_agro = -25
        for p in entities["entities"]:
            if p.health <= 0 or self.team == p.team:
                continue
            if control_agro > p.agro:
                continue

            if not Fun.wall_between(self.pos, p.pos, level) or self.wall_hack or p.status["Visible"] > 0:
                if p.status["Stealth"] > 0 and not p.status["Visible"] > 0:
                    continue
                detection_modifier = p.stealth_mod * self.stealth_counter

                if detection_modifier > 1: detection_modifier = 1
                if p.status["Visible"] > 0: detection_modifier = 1

                # Check if the potential target is in detection range
                if Fun.check_point_in_cone(target_check // 6 * detection_modifier,
                        self.pos[0], self.pos[1], p.pos[0], p.pos[1],
                        self.angle, self.targeting_angle * 3) or \
                        Fun.check_point_in_cone(target_check * detection_modifier,
                                            self.pos[0], self.pos[1], p.pos[0], p.pos[1],
                                            self.angle, self.targeting_angle)\
                        or Fun.check_point_in_circle(target_check // 10, self.pos[0], self.pos[1], p.pos[0], p.pos[1]):
                    self.target = p
                    self.is_target = True
                    control_agro = p.agro

        # Check for sounds
        if not self.target:
            for sound in entities["sounds"]:
                if self.team == sound.source:
                    continue
                if Fun.check_point_in_circle(sound.radius, sound.pos[0], sound.pos[1], self.pos[0], self.pos[1]):
                    self.angle = Fun.angle_between(sound.pos, self.pos)
    target_angle = 0
    target_pos = False
    wall_in = False

    if self.target:
        self.target.is_targeted = True
        # If the target is dead, reset targeting
        if self.target.health <= 0:
            self.target = False
            return target_pos, target_angle, wall_in

        target_angle = self.target.angle
        target_pos = self.target.pos.copy()
        # Pathfinding
        # results = pathfinding(self, level)
        results = universal_pathfinding(self, level, target_pos)
        if results:
            # entities["particles"].append(Fun.GrowingCircle(results, Fun.WHITE, 0, 1, 32, 8))
            target_pos = results
            wall_in = True

    return target_pos, target_angle, wall_in


def entity_target_detection_healer(self, entities, level):
    # Used by the enemy AI able to find targets
    # Might make them capable of patrolling

    if self.time % 240 == 0 or not self.target:
        self.is_target = False
        self.target = False
        target_check = self.targeting_range
        # I might have to remake the whole targeting system
        control_health = 1
        for p in entities["entities"]:
            if self.team != p.team and p != self:
                continue
            if control_health < p.health / p.max_health:
                continue
            if not Fun.wall_between(self.pos, p.pos, level) or self.wall_hack:

                # Check if the potential target is in detection range
                if Fun.check_point_in_cone(target_check // 6,
                        self.pos[0], self.pos[1], p.pos[0], p.pos[1], self.angle, self.targeting_angle * 3) or \
                        Fun.check_point_in_cone(target_check,
                                            self.pos[0], self.pos[1], p.pos[0], p.pos[1],
                                            self.angle, self.targeting_angle)\
                        or Fun.check_point_in_circle(target_check // 10, self.pos[0], self.pos[1], p.pos[0], p.pos[1]):
                    self.target = p
                    self.is_target = True
                    control_health = p.health / p.max_health
    target_angle = 0
    target_pos = False
    wall_in = False

    if self.target:
        # If the target is dead, reset targeting
        if self.target.health <= 0:
            self.target = False
            return target_pos, target_angle, wall_in

        target_angle = self.target.angle
        target_pos = self.target.pos.copy()
        # Pathfinding
        # results = pathfinding(self, level)
        results = universal_pathfinding(self, level, target_pos)
        if results:
            # entities["particles"].append(Fun.GrowingCircle(results, Fun.WHITE, 0, 1, 32, 8))
            target_pos = results
            wall_in = True

    return target_pos, target_angle, wall_in


def agro_system(self):
    if self.did_agro_raise > 0:
        self.did_agro_raise -= self.agro_decrease_rate
    elif self.agro > 0 and self.time % 4 == 0:
        self.agro -= 1


# |Ally fire control|---------------------------------------------------------------------------------------------------
def basic_fire_control(self, entities, level, target, wall_in):
    self.input["Shoot"] = random.randint(0, self.weapon.fire_rate) == 0 and \
                          Fun.check_point_in_circle_new(self.weapon.range * 0.8, self.pos, target) and \
                          not wall_in
    # Reloading
    self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0


def lord_fire_control(self, entities, level, target, wall_in):
    basic_fire_control(self, entities, level, target, wall_in)

    self.input["Skill 2"] = entity_get_enemy_count(self, entities, goal=5, dist=256) and \
                            self.ai_state in ["Hold", "Attack", "Freely"]
    self.input["Skill 1"] = Fun.distance_between(target, self.pos) < 128


def gunblade_fire_control(self, entities, level, target, wall_in):
    if not melee_fire_control(self, entities, level, target, wall_in):
        self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0
        entity_shoot_with_startup_lag(self, Fun.distance_between(target, self.pos), 7 * 30)
        if self.free_var['Startup lag'] > 0:
            # self.draw_aim_line = self.weapon.laser_sight
            self.input["Alt fire"] = True
            self.input["Shoot"] = start_up_lag_handler(self, self.free_var["Startup time"])
        return
    self.input["Skill 1"] = True
    self.input["Skill 2"] = entity_get_enemy_count(self, entities, goal=5, dist=256)


def emperor_gun_fire_control(self, entities, level, target, wall_in):
    if not basic_fire_control(self, entities, level, target, wall_in):
        self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0
        entity_shoot_with_startup_lag(self, Fun.distance_between(target, self.pos), 7 * 30)
        if self.free_var['Startup lag'] > 0:
            # self.draw_aim_line = self.weapon.laser_sight
            self.input["Alt fire"] = True
            self.input["Shoot"] = start_up_lag_handler(self, self.free_var["Startup time"])
        return
    self.input["Skill 1"] = True
    self.input["Skill 2"] = entity_get_enemy_count(self, entities, goal=5, dist=256)


def wizard_fire_control(self, entities, level, target, wall_in):
    basic_fire_control(self, entities, level, target, wall_in)

    skill_1 = self.skills[0]
    if skill_1.recharge >= skill_1.recharge_max:
        self.input["Shoot"] = False
        self.input["Skill 1"] = True
        self.input["Interact"] = random.random() < 0.25


def wizard_radio_fire_control(self, entities, level, target, wall_in):
    basic_fire_control(self, entities, level, target, wall_in)
    self.input["Alt fire"] = self.input["Shoot"]
    # Add an option to switch ammo type?

    skill_1 = self.skills[0]
    if skill_1.recharge >= skill_1.recharge_max:
        self.input["Shoot"] = False
        self.input["Skill 1"] = True
        self.input["Interact"] = random.random() < 0.25


def mortar_fire_control(self, entities, level, target, wall_in):
    basic_fire_control(self, entities, level, target, wall_in)
    self.input["Alt fire"] = self.input["Shoot"]


def condor_fire_control(self, entities, level, target, wall_in):
    basic_fire_control(self, entities, level, target, wall_in)
    self.input["Skill 1"] = Fun.distance_between(target, self.pos) < 128 and self.target.armour > 0


def condor_shotgun_fire_control(self, entities, level, target, wall_in):
    basic_fire_control(self, entities, level, target, wall_in)
    self.input["Alt fire"] = Fun.distance_between(target, self.pos) < 96
    self.input["Skill 1"] = Fun.distance_between(target, self.pos) < 128 and self.target.armour > 0


def melee_fire_control(self, entities, level, target, wall_in):
    if Fun.distance_between(target, self.pos) <= self.weapon.range:
        # combo_stage = self.free_var[self.weapon.name]["Combo stage"]
        try:
            basic_thres = self.free_var[self.weapon.name]["basic threshold"]
            if type(basic_thres) == list:
                basic_thres = basic_thres[self.free_var[self.weapon.name]["Combo stage"]]
            self.input["Shoot"] = self.free_var[self.weapon.name]["Press time"] < basic_thres  # - 10 * combo_stage
        except KeyError:
            return False
        return True
    return False


def melee_fire_control_no_stopping(self, entities, level, target, wall_in):
    try:
        if Fun.distance_between(target, self.pos) <= self.weapon.range or self.free_var[self.weapon.name]["Press time"] > 0:
        # combo_stage = self.free_var[self.weapon.name]["Combo stage"]
            basic_thres = self.free_var[self.weapon.name]["basic threshold"]
            if type(basic_thres) == list:
                basic_thres = basic_thres[self.free_var[self.weapon.name]["Combo stage"]]
            self.input["Shoot"] = self.free_var[self.weapon.name]["Press time"] < basic_thres # or self.free_var[f"{self.weapon.name}"]["Press time"] > 0 # - 10 * combo_stage

            return True
        return False
    except KeyError:
        return False


def chain_axe_fire_control(self, entities, level, target, wall_in):
    dist = Fun.distance_between(target, self.pos)
    if dist <= 128:
        self.input["Shoot"] = self.weapon.free_var["Press time"] < dist
    else:
        # smoke screen when he's targeted and not in range to attack
        allow = False
        for e in entities["entities"]:
            if e.target != self:
                continue
            allow = True
            break
        self.input["Skill 2"] = allow


def hook_swords_fire_control(self, entities, level, target, wall_in):
    dist = Fun.distance_between(target, self.pos)
    melee_fire_control(self, entities, level, target, wall_in)
    if not dist <= 128:
        # smoke screen when he's targeted and not in range to attack
        allow = False
        for e in entities["entities"]:
            if e.target != self:
                continue
            allow = True
            break
        self.input["Skill 2"] = allow


def gun_fu_fire_control(self, entities, level, target, wall_in):
    dist = Fun.distance_between(target, self.pos)
    if dist <= self.weapon.range:
        self.input["Shoot"] = self.time % self.weapon.fire_rate * 3 == 0
        self.input["Alt fire"] = dist <= 128
    else:
        # smoke screen when he's targeted and not in range to attack
        allow = False
        for e in entities["entities"]:
            if e.target != self:
                continue
            allow = True
            break
        self.input["Skill 2"] = allow


def medic_rifle_fire_control(self, entities, level, target, wall_in):
    if self.target.health < self.target.max_health - self.weapon.bullet_info[3]:
        self.input["Shoot"] = random.randint(0, self.weapon.fire_rate) == 0 and \
                              Fun.check_point_in_circle_new(self.weapon.range * 0.33, self.pos, target) and \
                              not wall_in
    # Reloading
    self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0


def stretcher_fire_control(self, entities, level, target, wall_in):
    self.input["Shoot"] = Fun.check_point_in_circle_new(self.weapon.range * 1.1, self.pos, target)
    # Reloading
    # self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0


def shield_generator_fire_control(self, entities, level, target, wall_in):
    self.input["Shoot"] = random.randint(0, self.weapon.fire_rate) == 0 and \
                          Fun.check_point_in_circle_new(self.weapon.range * 0.8, self.pos, target) and \
                          not wall_in
    # Reloading
    # self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0


def war_and_peace_fire_control(self, entities, level, target, wall_in):
    self.input["Shoot"] = random.randint(0, self.weapon.fire_rate) == 0 and \
                          Fun.check_point_in_circle_new(self.weapon.range, self.pos, target) and \
                          not wall_in
    self.input["Alt fire"] = Fun.check_point_in_circle_new(self.weapon.range * 1.2, self.pos, target)
    # Reloading
    self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0


def cutlass_fire_control(self, entities, level, target, wall_in):
    if not melee_fire_control(self, entities, level, target, wall_in):
        self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0
        entity_shoot_with_startup_lag(self, Fun.distance_between(target, self.pos), 6 * 80)
        if self.free_var['Startup lag'] > 0:
            # self.draw_aim_line = self.weapon.laser_sight
            self.input["Alt fire"] = True
            self.input["Shoot"] = start_up_lag_handler(self, self.free_var["Startup time"])
    self.input["Skill 1"] = True
    self.input["Skill 2"] = entity_get_enemy_count(self, entities, goal=5, dist=256)


def vivianne_fire_control(self, entities, level, target, wall_in):
    self.input["Shoot"] = random.randint(0, self.weapon.fire_rate) == 0 and \
                          Fun.check_point_in_circle_new(self.weapon.range * 0.8, self.pos, target) and \
                          not wall_in
    # Reloading
    self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0
    self.input["Skill 1"] = entity_get_enemy_count(self, entities, goal=2, dist=512) and random.random() < 0.5
    self.input["Skill 2"] = not self.input["Skill 1"]


def vivianne_melee_fire_control(self, entities, level, target, wall_in):
    melee_fire_control(self, entities, level, target, wall_in)
    self.input["Skill 1"] = entity_get_enemy_count(self, entities, goal=2, dist=512) and random.random() < 0.5
    self.input["Skill 2"] = not self.input["Skill 1"]


def c4_fire_control(self, entities, level, target, wall_in):
    self.input["Shoot"] = random.randint(0, self.weapon.fire_rate*8) == 0 and \
                          Fun.check_point_in_circle_new(self.weapon.range * 0.8, self.pos, target) and \
                          not wall_in
    # Reloading
    self.input["Reload"] = self.weapon.ammo == Fun.get_random_element_from_list([7, 4, 0]) and self.weapon.ammo_pool > 0


def fortress_fire_control(self, entities, level, target, wall_in):
    basic_fire_control(self, entities, level, target, wall_in)
    if self.driving == 4:
        if Fun.distance_between(self.pos, target) < 128:
            self.input["Dash"] = self.angle - 9 < self.free_var["Move angle"] < self.angle + 9


def buggy_fire_control(self, entities, level, target, wall_in):
    self.input["Shoot"] = random.randint(0, self.weapon.fire_rate) == 0 and \
                          Fun.check_point_in_cone(
                              self.weapon.range * 0.8, self.pos[0], self.pos[1],
                              target[0], target[1], self.free_var["Move angle"], 30) and \
                          not wall_in
    # Reloading
    self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0
    if self.driving == 4:
        if Fun.distance_between(self.pos, target) < 128:
            self.input["Dash"] = self.angle - 9 < self.free_var["Move angle"] < self.angle + 9


ALLY_FIRE_CONTROL = {
    "Lord": {
        "Saloum Mk-2": lord_fire_control,
        "GMG-04B": lord_fire_control,
        "Big Iron": lord_fire_control},
    "Emperor": {
        "GunBlade": gunblade_fire_control,
        "Corrine's Old Rifle": emperor_gun_fire_control,
        "Oversized stun baton": gunblade_fire_control},
    "Wizard": {
        "Jeanne's Family Shotgun": wizard_fire_control,
        "Custom Mk18 Laser cutter": wizard_fire_control,
        "Crippled Laddie FCS Radio": wizard_radio_fire_control},
    "Sovereign": {
        "St-Maurice": basic_fire_control,
        "St-Laurent Gen 1": basic_fire_control,
        "Mk16 Flare Mortar": mortar_fire_control},
    "Duke": {
        "Chain Axe": chain_axe_fire_control,
        "Hook Swords": hook_swords_fire_control,
        "Gun and Ballistic Knife": gun_fu_fire_control},
    "Jester": {
        "Epicurean Medic Rifle": medic_rifle_fire_control,
        "Nihilist Stretcher": stretcher_fire_control,
        "Stoic Shield generator": shield_generator_fire_control},
    "Condor": {
        "Type 41 SMG": condor_fire_control,
        "Type 23 Shotgun": condor_shotgun_fire_control, # Give a way to use the shield later.
        "Type 47 Rifle": condor_fire_control},

    "Curtis": {
        "Standard Shotgun": basic_fire_control,
        "War and Peace": war_and_peace_fire_control,
        "Hunk of Steel": melee_fire_control},

    "Doppelgänger": {
        "Standard Shotgun": basic_fire_control,
        "War and Peace": war_and_peace_fire_control,
        "Hunk of Steel": melee_fire_control},
    "Lawrence": {
        "Lawrence's Cutlass & Flintlock": cutlass_fire_control,
        "Captain's Axe & Blunderbuss": cutlass_fire_control,
        "Musket .360": cutlass_fire_control},
    "Mark": {
        "Mark's Real Rifle": basic_fire_control,
        "Type 30 Rifle": basic_fire_control,
        "C4": c4_fire_control},
    "Vivianne": {
        "Vivianne's Rifle": vivianne_fire_control,
        "Vivianne's Shotgun": vivianne_fire_control,
        "Vivianne's Leg": vivianne_melee_fire_control},

    "Fortress": {"Fortress Machine Gun": fortress_fire_control},
    "Sand Buggy": {"Buggy Gun": buggy_fire_control},
}


# |Ally Skill Control|--------------------------------------------------------------------------------------------------
def basic_skill_control(self, entities, level):
    pass


def wizard_skill_control(self, entities, level):
    lord_in_beast_mode = False
    enemy_count = 0
    for e in entities["entities"]:
        if e.team == self.team:
            if e.name == "Lord":
                if e.skills[1].active:
                    lord_in_beast_mode = True
                    break
            continue
        if Fun.distance_between(e.pos, self.pos) < 512:
            enemy_count += 1
            if enemy_count > 10:
                break

    self.input["Skill 2"] = lord_in_beast_mode or enemy_count > 10


def sovereign_skill_control(self, entities, level):
    allow_skill_1 = True
    for e in entities["entities"]:
        if e.target == self:
            allow_skill_1 = False
            break

    self.input["Skill 1"] = self.reloading and allow_skill_1
    self.input["Skill 2"] = not self.target


def duke_skill_control(self, entities, level):
    # tail swipe when there multiple bullets around the area of effect,
    self.input["Skill 1"] = entity_get_enemy_count(self, entities, goal=2, dist=64, entity_type="bullets")


def jester_skill_control(self, entities, level):
    enemies_around = entity_get_enemy_count(self, entities, goal=0, dist=128, entity_type="entities")

    allow_discharge = "Surge Protection" in self.free_var or not entity_get_ally_count(self, entities, goal=1, dist=128, entity_type="entities")
    self.input["Skill 1"] = allow_discharge and enemies_around
    self.input["Skill 2"] = enemies_around


def condor_skill_control(self, entities, level):
    self.input["Skill 2"] = self.health <= self.max_health * 0.075


def curtis_skill_control(self, entities, level):
    # tail swipe when there multiple bullets around the area of effect,
    self.input["Skill 1"] = entity_get_enemy_count(self, entities, goal=0, dist=80, entity_type="bullets")


def mark_skill_control(self, entities, level):
    allow_skill_1 = False
    for e in entities["entities"]:
        if e.target == self:
            allow_skill_1 = True
            break

    self.input["Skill 1"] = not self.target
    self.input["Skill 2"] = allow_skill_1


def fortress_skill_control(self, entities, level):
    if self.driving < 3: return
    self.input["Skill 2"] = not entity_get_enemy_count(self, entities, goal=0, dist=256)


# Handle skills that Are not handled by fire control
ALLY_SKILL_CONTROL = {
    "Lord": basic_skill_control,
    "Emperor": basic_skill_control,
    "Wizard": wizard_skill_control,
    "Sovereign": sovereign_skill_control,
    "Duke": duke_skill_control,
    "Jester": jester_skill_control,
    "Condor": condor_skill_control,

    "Curtis": curtis_skill_control,
    "Doppelgänger": curtis_skill_control,
    "Lawrence": basic_skill_control,
    "Mark": mark_skill_control,
    "Vivianne": basic_skill_control
}


# |Ally input|----------------------------------------------------------------------------------------------------------
def test_ally_input(self, entities, level):
    self.input = Fun.get_default_inputs()
    {"Follow": ally_sub_input_follow,
     "Hold": ally_sub_input_hold,
     "Attack": ally_sub_input_attack,
     "Freely": ACT_FREELY_DICT[self.name]}[self.ai_state](self, entities, level)


def ally_sub_input_follow(self, entities, level):
    # Make it stay on the position to hold
    move_target = universal_pathfinding(self, level, self.free_var["Ally waypoint"].pos)
    aaa = bool(move_target)
    if not move_target:
        move_target = self.free_var["Ally waypoint"].pos
    self.mouse_pos = self.free_var["Ally waypoint"].mouse_pos.copy()
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 48)
    if not aaa: entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def ally_sub_input_hold(self, entities, level):
    move_target = universal_pathfinding(self, level, self.free_var["Ally waypoint"])

    if not move_target:
        move_target = self.free_var["Ally waypoint"]
    self.mouse_pos = move_target.copy()

    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    # Make it stay on the position to hold
    if target:
        aim_target = self.target.pos.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        # modify position of target for some ia types
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 16)
    # entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def ally_sub_input_attack(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        # move_target = target.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)

        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        entity_move_toward_point(self, aim_target, self.weapon.range * 0.8)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    # entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 32)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)

    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def jester_input(self, entities, level):
    self.input = Fun.get_default_inputs()
    # When he gets new weapons, use a dict to choose sub inputs
    #
    {"Follow": {
        "Epicurean Medic Rifle": jester_sub_input_follow,
        "Nihilist Stretcher": ally_sub_input_follow,
        "Stoic Shield generator": ally_sub_input_follow}[self.weapon.name],
     "Hold": {
        "Epicurean Medic Rifle": jester_sub_input_hold,
        "Nihilist Stretcher": ally_sub_input_hold,
        "Stoic Shield generator": ally_sub_input_hold}[self.weapon.name],
     "Attack": {
        "Epicurean Medic Rifle": jester_sub_input_attack,
        "Nihilist Stretcher": ally_sub_input_attack,
        "Stoic Shield generator": ally_sub_input_attack}[self.weapon.name],
     "Freely": ACT_FREELY_DICT[self.name]}[self.ai_state](self, entities, level)


def jester_sub_input_follow(self, entities, level):
    # Make it stay on the position to hold
    move_target = universal_pathfinding(self, level, self.free_var["Ally waypoint"].pos)
    aaa = bool(move_target)
    if not move_target:
        move_target = self.free_var["Ally waypoint"].pos
    self.mouse_pos = self.free_var["Ally waypoint"].mouse_pos.copy()
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection_healer(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 48)
    if not aaa: entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def jester_sub_input_hold(self, entities, level):
    move_target = universal_pathfinding(self, level, self.free_var["Ally waypoint"])

    if not move_target:
        move_target = self.free_var["Ally waypoint"]
    self.mouse_pos = move_target.copy()

    target, target_angle, wall_in = entity_target_detection_healer(self, entities, level)
    # Make it stay on the position to hold
    if target:
        aim_target = self.target.pos.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        # modify position of target for some ia types
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 16)
    # entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def jester_sub_input_attack(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection_healer(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        move_target = target.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)

        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)

    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


# Act freely functions
def ally_sub_input_roam(self, entities, level):
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        move_target = universal_pathfinding(self, level, self.target.pos)
        aaa = bool(move_target)
        if not move_target:
            move_target = self.target.pos
        self.mouse_pos = self.target.mouse_pos.copy()
        entity_move_toward_point(self, move_target, 48)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    else:
        m_target = self.pos.copy()
        for e in entities["entities"]:
            if e.team == self.team: continue
            if Fun.distance_between(self.pos, e.pos) > 320:
                m_target = e.pos.copy()
        move_target = universal_pathfinding(self, level, m_target)
        aaa = bool(move_target)
        if not move_target:
            move_target = m_target
        self.mouse_pos = m_target

        entity_move_toward_point(self, move_target, 128)
        if not aaa: entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def ally_sub_input_focus_objective(self, entities, level):
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        move_target = universal_pathfinding(self, level, self.target.pos)
        aaa = bool(move_target)
        if not move_target:
            move_target = self.target.pos
        self.mouse_pos = self.target.mouse_pos.copy()
        entity_move_toward_point(self, move_target, 48)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    else:
        if level['objective points']:
            m_target = level['objective points'][0]
            dist = 32
        else:
            dist = 128
            m_target = self.pos.copy()
            for e in entities["entities"]:
                if e.team == self.team: continue
                if Fun.distance_between(self.pos, e.pos) > 320:
                    m_target = e.pos.copy()
                    break
        move_target = universal_pathfinding(self, level, m_target)
        aaa = bool(move_target)
        if not move_target:
            move_target = m_target
        self.mouse_pos = m_target

        entity_move_toward_point(self, move_target, dist)
        if not aaa: entity_spread_apart(self, entities)

    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def ally_sub_input_wizard(self, entities, level):
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold

    main_group = entity_find_main_group(self, entities, dist=256)
    move_target = universal_pathfinding(self, level, main_group)
    aaa = bool(move_target)
    if not move_target:
        move_target = main_group
    mod_move_target = move_target.copy()
    self.mouse_pos = main_group.copy()
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        mod_move_target = Fun.move_with_vel_angle(move_target, 128, self.angle - 180)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 96)
    entity_move_toward_point(self, mod_move_target, 32)
    # if not aaa: entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def ally_sub_input_sniper(self, entities, level):
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold
    move_target = universal_pathfinding(self, level, self.free_var["Ally waypoint"].pos)
    aaa = bool(move_target)
    if not move_target:
        move_target = self.free_var["Ally waypoint"].pos
    self.mouse_pos = self.free_var["Ally waypoint"].mouse_pos.copy()
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 224)
    if not aaa: entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def ally_sub_input_duke(self, entities, level):
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold

    # Try to find Corrine
    main_group = entity_find_teammate(self, entities, target="Sovereign")
    dist = 32
    if not main_group:
        main_group = self.free_var["Ally waypoint"].pos
        dist = 120

    move_target = universal_pathfinding(self, level, main_group)
    aaa = bool(move_target)
    if not move_target:
        move_target = main_group
    mod_move_target = move_target.copy()
    self.mouse_pos = main_group.copy()
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        mod_move_target = Fun.move_with_vel_angle(move_target, 128, self.angle)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 96)
    entity_move_toward_point(self, mod_move_target, 32)
    # if not aaa: entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, dist)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def ally_sub_input_jester(self, entities, level):
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold

    target, target_angle, wall_in = entity_target_detection_healer(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)

        move_target = universal_pathfinding(self, level, self.target.pos)
        aaa = bool(move_target)
        if not move_target:
            move_target = self.target.pos
        self.mouse_pos = self.target.mouse_pos.copy()
        entity_move_toward_point(self, move_target, 48)
        if not aaa: entity_spread_apart(self, entities, spread_dist=48)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def ally_sub_input_condor(self, entities, level):
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold

    main_group = entity_find_main_group(self, entities, dist=256)
    move_target = universal_pathfinding(self, level, main_group)
    aaa = bool(move_target)
    if not move_target:
        move_target = main_group
    mod_move_target = move_target.copy()
    self.mouse_pos = main_group.copy()
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        mod_move_target = Fun.move_with_vel_angle(move_target, 128, self.angle)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 96)
    entity_move_toward_point(self, mod_move_target, 32)
    # if not aaa: entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def ally_sub_input_lawrence(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    self.input = Fun.get_default_inputs()
    if target:
        aim_target = self.target.pos.copy()
        move_target = target.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_maintain_weapon_range(self, Fun.distance_between(target, self.pos), move_target, 256, get_away=192)
        entity_dash_when_targeted(self, no_shoot_threshold=50, threshold=0.75)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)

    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


# Fortress
def vehicle_escort(self, level):
    if 'APC path' in level['free var']:
        if level['free var']['APC path']:
            move_target = level['free var']['APC path'][0]  # Get first point from the list
            if Fun.distance_between(move_target, self.pos) < self.thiccness:
                # Remove current point from the list
                level['free var']['APC path'].pop(0)
            if self.is_player: return
            if self.ai_state != "Hold":
                # Stops moving if there's enemies too close
                APC_MOVE_TO_POINT[self.free_var["IS AN APC"]](self, move_target, 8)



def fortress_input(self, entities, level):
    self.input = Fun.get_default_inputs()
    # If it doesn't act like a normal ally
    {"Follow": fortress_sub_input_follow,
     "Hold": fortress_sub_input_hold,
     "Attack": fortress_sub_input_attack,
     "Freely": fortress_sub_input_attack}[self.ai_state](self, entities, level)
    self.input["Alt fire"] = self.driving >= 2
    # Check if it has objectives to follow, if yes override every order expect hold
    #


APC_MOVE_TO_POINT = { # Add something to choose between weapons later
    "Fortress": fortress_move_toward_point,
    "Sand Buggy": buggy_move_toward_point
}

def fortress_sub_input_follow(self, entities, level):
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold
    move_target = universal_pathfinding(self, level, self.free_var["Ally waypoint"].pos)
    aaa = bool(move_target)
    if not move_target:
        move_target = self.free_var["Ally waypoint"].pos
    self.mouse_pos = self.free_var["Ally waypoint"].mouse_pos.copy()
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        self.mouse_pos = aim_target.copy()
        fortress_fire_control(self, entities, level, target, wall_in)

        ALLY_FIRE_CONTROL[self.free_var["IS AN APC"]][self.weapon.name](self, entities, level, target, wall_in)
        self.input["Skill 1"] = self.driving >= 1

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    fortress_skill_control(self, entities, level)
    APC_MOVE_TO_POINT[self.free_var["IS AN APC"]](self, move_target, 64)
    # fortress_move_toward_point(self, move_target, 64)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def fortress_sub_input_hold(self, entities, level):
    self.input = Fun.get_default_inputs()
    move_target = universal_pathfinding(self, level, self.free_var["Ally waypoint"])

    if not move_target:
        move_target = self.free_var["Ally waypoint"]
    self.mouse_pos = move_target.copy()

    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    # Make it stay on the position to hold
    if target:
        aim_target = self.target.pos.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        # modify position of target for some ia types
        ALLY_FIRE_CONTROL[self.free_var["IS AN APC"]][self.weapon.name](self, entities, level, target, wall_in)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    fortress_skill_control(self, entities, level)
    APC_MOVE_TO_POINT[self.free_var["IS AN APC"]](self, move_target, 64)
    # fortress_move_toward_point(self, move_target, 64)
    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def fortress_sub_input_attack(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    self.input = Fun.get_default_inputs()
    if target:
        aim_target = self.target.pos.copy()
        move_target = target.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)

        ALLY_FIRE_CONTROL[self.free_var["IS AN APC"]][self.weapon.name](self, entities, level, target, wall_in)

        APC_MOVE_TO_POINT[self.free_var["IS AN APC"]](self, move_target, 64)
        # fortress_move_toward_point(self, move_target, 64)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    fortress_skill_control(self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


# |Ally Draw|-----------------------------------------------------------------------------------------------------------
def player_draw(self, WIN, scrolling):
    # Draw the colision box
    # Get the sprite direction
    player_direction = Fun.get_entity_direction(self.angle) % 6
    weapon_angle = self.angle
    if not self.standing_still:
        player_direction = Fun.get_entity_direction(self.direction_angle) % 6

    # Affect the placement of the second weapon
    # weapon_x_mod, weapon_y_mod, weapon_angle_mod = 2, 4, 10

    # Draws the player
    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0] - 16 + scrolling[0], self.pos[1] + 11 + scrolling[1]),
             special_flags=pg.BLEND_RGBA_SUB)
    self.draw_player(scrolling, WIN, player_direction)

    # Draw the weapon
    draw_weapon(self, WIN, scrolling)


def fortress_draw(self, WIN, scrolling):
    Fun.draw_spritestack(WIN, Fun.SPRITE_FORTRESS_APC_CHASSIS, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                         self.free_var["Move angle"] + 90, height_diff=0.5)
    # 226
    # angle = 226 + self.free_var["Move angle"]
    pos = [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1] - 16]
    angle = self.free_var["Move angle"] + 226 - 180
    pos = Fun.move_with_vel_angle(pos, 22.6274, angle)
    Fun.draw_spritestack(WIN, Fun.SPRITE_FORTRESS_APC_TURRET, pos, self.aim_angle + 90, height_diff=0.5)


def buggy_draw(self, WIN, scrolling):
    # Fun.draw_spritestack(WIN, Fun.SPRITE_SAND_BUGGY, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
    #                      self.free_var["Move angle"] + 90, height_diff=0.5)

    pos = [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]]
    angle = Fun.angle_value_limiter(self.free_var["Move angle"] + 90)

    # t_angle = Fun.angle_value_limiter(self.free_var["Target Move angle"] + 90)
    t_angle = Fun.pg.math.clamp(self.free_var["Target Move angle"] + 90,
                                      angle - 25, angle + 25)
    # t_angle = self.free_var["Target Move angle"] + 90
    # smaller_angle = angle - 30
    # bigger_angle = angle + 30
    # if the direction the AI is looking at is near -180/180
    # if 180 - 30 > angle and 180 - 30 > t_angle: t_angle = smaller_angle
    # elif smaller_angle < t_angle: t_angle = smaller_angle
    # if angle > -180 + 30 and t_angle > -180 + 30: t_angle = bigger_angle
    # elif t_angle < bigger_angle: t_angle = bigger_angle
    # check

    height_diff = 0.5
    sprites = Fun.SPRITE_SAND_BUGGY.copy()
    mod = 0
    if self.input["Down"]:
        mod = 3
    front_wheel_rotation = abs(mod - (round(self.time // 4 * self.free_var["Move vel"]) % 4))

    for count, s in enumerate(Fun.SPRITE_SAND_BUGGY_WHEEL[front_wheel_rotation]):
        sprites[count].blit(s, [0, 0])

    for i, sprite in enumerate(sprites):
        rotated_sprite = pg.transform.rotate(sprite, -angle)
        WIN.blit(rotated_sprite, (pos[0] - rotated_sprite.get_width() // 2, pos[1] - rotated_sprite.get_height() // 2 - height_diff * i))
        if i < len(Fun.SPRITE_SAND_BUGGY_FRONT[front_wheel_rotation]):
            rotated_sprite = pg.transform.rotate(Fun.SPRITE_SAND_BUGGY_FRONT[front_wheel_rotation][i], -t_angle)
            WIN.blit(rotated_sprite, Fun.move_with_vel_angle(
                (pos[0] - rotated_sprite.get_width() // 2, pos[1] - rotated_sprite.get_height() // 2 - height_diff * i), 28, angle - 90)
                     )

    pos = [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1] - 14]
    angle = self.free_var["Move angle"] - 180
    pos = Fun.move_with_vel_angle(pos, 24, angle)

    Fun.draw_spritestack(WIN, Fun.SPRITE_SAND_BUGGY_TURRET,
                         pos,
                         self.aim_angle + 90, height_diff=0.5)
    # SPRITE_SAND_BUGGY_TURRET


def cardboard_box_draw(self, WIN, scrolling):
    Fun.draw_spritestack(WIN, Fun.SPRITE_CARDBOARD_BOX, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                         self.skills[0].free_var["Draw angle"] + 90, height_diff=0.75)


# |Ally On Death|-------------------------------------------------------------------------------------------------------
def lord_on_death(self, entities, level):
    if 'Super Duper Ultimate Death Defying Plus Ultra Supreme Heavenly Beast Mode DELUXE' in self.free_var:
        # Lord cannot die during the duration, still takes damage but doesn't go under 1
        if self.skills[1].active:
            self.health = 1


def condor_on_death(self, entities, level):
    # print(self.status["Last Stand"])
    if self.status["Last Stand"] > 0:
        self.health = round(self.max_health * 0.33)
        self.status["No damage"] = 60 * 3
        self.status["No debuff"] = 60 * 3
        self.status["Last Stand"] = 0

        number_of_particle = 18
        for particles_to_add in range(360 // number_of_particle):
            entities["particles"].append(Fun.RandomParticle2(
                [self.pos[0], self.pos[1]], Fun.DARK_RED, 1 + 3 * random.random(), random.randint(45, 90),
                                                        particles_to_add * number_of_particle,
                size=Fun.get_random_element_from_list([3, 4, 6])))

        Fun.play_sound("Skill 7")
        for u in self.upgrades:
            if u.name == "Unbreaking Blue Balls":
                u.free_var = {"Last Stand": True}
                break
    # print(self.health)


def fortress_on_death(self, entities, level):
    level["events"].append(MissionEvent("", trigger_constant, True, [loss_of_apc]))


# |Enemy Input|---------------------------------------------------------------------------------------------------------
# Testing
def enemy_input_nest_trooper(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    self.input = Fun.get_default_inputs()
    if target:
        aim_target = self.target.pos.copy()
        move_target = target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        # modify position of target for some ia types

        og_dist = Fun.distance_between(target, self.pos)
        range_target = og_dist > self.weapon.range * 0.65
        if range_target:
            self.input["Right"] = self.pos[0] < move_target[0]
            self.input["Left"] = self.pos[0] > move_target[0]
            self.input["Down"] = self.pos[1] < move_target[1]
            self.input["Up"] = self.pos[1] > move_target[1]

        if og_dist < self.weapon.range * 0.3:
            self.input["Right"] = self.pos[0] > move_target[0]
            self.input["Left"] = self.pos[0] < move_target[0]
            self.input["Down"] = self.pos[1] > move_target[1]
            self.input["Up"] = self.pos[1] < move_target[1]

        # Check if something is in range
        if random.randint(0, self.weapon.fire_rate) == 0 and Fun.check_point_in_circle(
                self.weapon.range * 0.8, self.pos[0], self.pos[1], target[0], target[1]) and not wall_in:
            self.input["Shoot"] = True
        if self.weapon.weapon_class == "Melee":
            if Fun.distance_between(target, self.pos) <= self.weapon.range:
                # combo_stage = self.free_var[self.weapon.name]["Combo stage"]
                self.input["Shoot"] = self.free_var[self.weapon.name]["Press time"] < 40 #  - 10 * combo_stage

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


# Faction 1
def enemy_input_faction_1_basic(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.65, get_away=64)
        entity_shoot_with_startup_lag(self, og_dist, self.weapon.range * 1.1)
        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_shoot_startup_handler(self)

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_1_body_guard(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            entity_maintain_weapon_range(self, og_dist, true_target, self.weapon.range * 0.65, get_away=64)
            entity_shoot_with_startup_lag(self, og_dist, self .weapon.range * 1.1)
        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_shoot_startup_handler(self)
    entity_move_toward_point(self, true_target, 96)
    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_1_heavy_sniper(self, entities, level):
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.65, get_away=64)
            entity_shoot_with_startup_lag(self, og_dist, self.weapon.range * 1.1)
        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True
    else:
        entity_dodge_bullets(self, entities, look_range=64)

    entity_shoot_startup_handler(self)

    entity_move_toward_point(self, true_target, 96)
    entity_spread_apart(self, entities)
    Fun.stunned_manager(self)
    return target, target_angle


def enemy_input_faction_1_radar(self, entities, level):
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        entity_maintain_weapon_range(self, og_dist, move_target, 512, get_away=128)

    entity_escort_ally(self, entities, level, escort_list=["Missile Operator"], escort_dist=48, look_dist=128)
    entity_dodge_bullets(self, entities, look_range=64)

    entity_spread_apart(self, entities)
    Fun.stunned_manager(self)
    return target, target_angle


def enemy_input_faction_1_missile(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.65, get_away=64)
            entity_shoot_no_startup_lag(self, og_dist, self.weapon.range * 1.1)

        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_move_toward_point(self, true_target, 96)
    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_2_basic(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            mod = 1
            # if self.reloading: mod = 3
            self.mouse_pos = self.target.pos
            entity_move_toward_point(self, true_target, 96)
            entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.98 * mod, get_away=self.weapon.range * 0.75 * mod)
            entity_shoot_no_startup_lag(self, og_dist, self.weapon.range * 1.1)
        entity_dodge_bullets(self, entities, 32)
        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_2_boomstick(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            mod = 1
            if self.reloading: mod = 3
            self.mouse_pos = self.target.pos
            entity_move_toward_point(self, true_target, 96)
            entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.98 * mod, get_away=self.weapon.range * 0.75 * mod)
            entity_shoot_with_startup_lag(self, og_dist, self.weapon.range * 1.1)

        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_shoot_startup_handler(self)
    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_2_smoker(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            mod = 1
            # if self.reloading: mod = 3
            self.mouse_pos = self.target.pos
            entity_move_toward_point(self, true_target, 96)
            entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.98 * mod, get_away=self.weapon.range * 0.75 * mod)
            entity_shoot_no_startup_lag(self, og_dist, self.weapon.range * 1.1)
        entity_dodge_bullets(self, entities, 32)
        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True
    entity_escort_ally(self, entities, level, escort_list=("VIP", "BoomStick"), escort_dist=48, look_dist=256)

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_2_crusher(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            mod = 1
            # if self.reloading: mod = 3
            self.mouse_pos = self.target.pos
            entity_move_toward_point(self, true_target, 96)
            entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.66 * mod, get_away=self.weapon.range * 0.25 * mod)
            melee_fire_control(self, entities, level, target, wall_in)
        entity_dodge_bullets(self, entities, 32)
        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_2_assassin(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            mod = 1
            # if self.reloading: mod = 3
            self.mouse_pos = self.target.pos
            entity_move_toward_point(self, Fun.move_with_vel_angle(true_target, 16, target_angle - 180), 80)
            entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.66 * mod, get_away=self.weapon.range * 0.25 * mod)
            #
            melee_fire_control_no_stopping(self, entities, level, target, wall_in)
        entity_dodge_bullets(self, entities, 32)
        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_3_basic(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            mod = 1
            if self.reloading: mod = 3
            self.mouse_pos = self.target.pos
            entity_move_toward_point(self, true_target, 96)
            entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.98 * mod, get_away=self.weapon.range * 0.75 * mod)
            entity_shoot_no_startup_lag(self, og_dist, self.weapon.range * 1.1)

        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_3_spotter(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        # true_target = universal_pathfinding(self, level, move_target)
        # if not true_target:
        #     true_target = move_target
            # entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.98, get_away=self.weapon.range * 0.75)
            # entity_shoot_no_startup_lag(self, og_dist, 256)
        #     self.input["Shoot"] = True
        #     entity_move_toward_point(self, true_target, 96)

        # Reloading

    entity_escort_ally(self, entities, level, escort_list=("VIP", "Artilleryman", "Bulwark"), escort_dist=48, look_dist=256)
    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_3_artilleryman(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            # entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.98, get_away=self.weapon.range * 0.75)
            # entity_shoot_no_startup_lag(self, og_dist, 256)
            self.input["Shoot"] = True
            entity_move_toward_point(self, true_target, 96)

        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_3_grenade(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            mod = 1
            if self.reloading: mod = 3
            self.mouse_pos = self.target.pos
            entity_move_toward_point(self, true_target, 96)
            entity_maintain_weapon_range(self, og_dist, move_target, 196 * 0.98 * mod, get_away=196 * 0.75 * mod)
            entity_shoot_no_startup_lag(self, og_dist, 196 * 1.1)

        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_3_bulwark(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 1.2, get_away=64)
        entity_shoot_no_startup_lag(self, og_dist, self.weapon.range * 1.6)

        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_move_toward_point(self, true_target, 96)
    entity_spread_apart(self, entities)
    # Stunning it doesn't disable it

    return target, target_angle


# |Enemy Act|-----------------------------------------------------------------------------------------------------------
def enemy_act_type_1(self, entities, level):
    # Get the inputs
    # target, target_angle = self.func_get_input(self, entities, {"enemies": []}, level)

    Fun.aim_system(self, self.weapon)

    # Do shit
    Fun.movement_entity(self)

    # I am placing the passive effects of enemies in the passive slot to not have to make more act functions
    self.weapon.passive(self, entities, level)
    self.crit = False
    # Gun
    if self.no_shoot_state == 0:
        self.reloading = False
        self.shooting = False
        if self.input["Alt fire"]:
            self.weapon.alt_fire(self, entities, level)
        if self.input["Shoot"] and self.weapon.ammo > 0:
            self.shooting = True
            self.shoot_bullet(entities, level)

        # Reloading
        if self.input["Reload"] and self.weapon.ammo_pool > 0:
            self.no_shoot_state, self.reloading = self.weapon.reload()
    else:
        self.shooting = False
        self.no_shoot_state -= 1

    # |Status effects|--------------------------------------------------------------------------------------------------
    Fun.status_manager(self, entities)

    # |Movement output|-------------------------------------------------------------------------------------------------
    Fun.movement_output(self, level)
    draw_aim_line(self, entities)
    if self.armour_break:
        # Need a sound effect
        self.armour_break = False


# |Enemy Draw|----------------------------------------------------------------------------------------------------------
def enemy_draw_basic(self, WIN, scrolling):
    # That one has animations
    if self.status["Stealth"] > 0:
        return
    # Draw the enemy
    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0]-16 + scrolling[0], self.pos[1] + 11 + scrolling[1]), special_flags=pg.BLEND_RGBA_SUB)
    enemy_direction = Fun.get_entity_direction(self.angle)
    # Fun.draw_entity(self, scrolling, WIN, enemy_direction)
    self.draw_player(scrolling, WIN, enemy_direction)

    # Draw the gun
    angle_to_add = 0
    if self.reloading:
        angle_to_add = (360 / self.weapon.reload_time) * self.no_shoot_state

    Fun.blitRotate(WIN, pg.transform.flip(self.weapon.sprite, True, -90 < self.aim_angle < 90),
                   Fun.move_with_vel_angle([self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]], 10,
                                           self.aim_angle),
                   [0, 0], 180 - self.aim_angle + angle_to_add)


def enemy_draw_advanced_gun(self, WIN, scrolling):
    # That one has animations
    if self.status["Stealth"] > 0:
        return
    # Draw the enemy
    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0]-16 + scrolling[0], self.pos[1] + 11 + scrolling[1]), special_flags=pg.BLEND_RGBA_SUB)
    enemy_direction = Fun.get_entity_direction(self.angle)
    # Fun.draw_entity(self, scrolling, WIN, enemy_direction)
    self.draw_player(scrolling, WIN, enemy_direction)

    # Draw the gun
    draw_weapon(self, WIN, scrolling)


def enemy_draw_sniper(self, WIN, scrolling):
    enemy_draw_basic(self, WIN, scrolling)
    #


def enemy_draw_enforcer(self, WIN, scrolling):
    # That one has animations
    if self.status["Stealth"] > 0:
        return
    # Draw the enemy

    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0]-16 + scrolling[0], self.pos[1] + 11 + scrolling[1]), special_flags=pg.BLEND_RGBA_SUB)
    Fun.draw_spritestack(WIN, Fun.SPRITE_ENFORCER, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]+8],
                         self.aim_angle + 90, height_diff=0.75)

    # Draw the gun
    angle_to_add = 0
    if self.reloading:
        angle_to_add = (360 / self.weapon.reload_time) * self.no_shoot_state

    Fun.blitRotate(WIN, pg.transform.flip(self.weapon.sprite, True, -90 < self.aim_angle < 90),
                   Fun.move_with_vel_angle([self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]], 10,
                                           self.aim_angle),
                   [0, 0], 180 - self.aim_angle + angle_to_add)
    #


def enemy_draw_bulwark(self, WIN, scrolling):
    # That one has animations
    if self.status["Stealth"] > 0:
        return
    # Draw the enemy

    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0]-16 + scrolling[0], self.pos[1] + 11 + scrolling[1]), special_flags=pg.BLEND_RGBA_SUB)
    frame_to_get = 0
    action_type = "Walk"
    # Make the counters go up
    for counter in self.animation_counter:
        if action_type == counter:
            self.animation_counter[counter] += 1
        else:
            self.animation_counter[counter] = 0
    # Sliding need a special case to handle its animation
    if not self.standing_still:
        # print(player_direction)
        frame_to_get = self.animation_counter[action_type] // 8 % 4
    Fun.draw_spritestack(WIN, Fun.SPRITE_BULWARKS[frame_to_get], [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]+10],
                         self.aim_angle + 90, height_diff=0.75)

    # Draw the gun
    angle_to_add = 0
    if self.reloading:
        angle_to_add = (360 / self.weapon.reload_time) * self.no_shoot_state

    Fun.blitRotate(WIN, pg.transform.flip(self.weapon.sprite, True, -90 < self.aim_angle < 90),
                   Fun.move_with_vel_angle([self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]], 10,
                                           self.aim_angle),
                   [0, 0], 180 - self.aim_angle + angle_to_add)
    #


# |On Death|------------------------------------------------------------------------------------------------------------
def enforcer_on_death(self, entities, level):
    Bullets.spawn_bullet(
        self, entities, Bullets.ExplosionSecondary, self.pos,
        0, [0, 30, 0, 20, {"Damage mod": 1, "Growth": 2, "Duration": 30}]
    )


# |Bosses|--------------------------------------------------------------------------------------------------------------
def hover_tank_input(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    # Find machine gun angle
    p_targets = {}
    for e in entities["entities"]:
        if e.team == self.team:
            continue
        if e.agro >= 0 and e.status["Stealth"] == 0:
            key = f"{e.agro}"
            if key not in p_targets:
                p_targets.update({key: [e]})
            else:
                p_targets[key].append(e)
    keys = list(p_targets.keys())
    keys.sort()
    self.free_var["Allow machine gun"] = False
    if p_targets:
        mod = -2
        if len(keys) == 1:
            mod = -1
        aaa = keys[mod]
        mg_target = p_targets[aaa][0]
        mg_target = mg_target.pos
        self.free_var["Allow machine gun"] = Fun.distance_between(mg_target, [self.pos[0], self.pos[1]-18]) < 40 * 7
        self.free_var["Machine Gun Angle"] = Fun.angle_value_limiter(
            Fun.move_angle(
                Fun.angle_between(mg_target, [self.pos[0], self.pos[1]-18]), self.free_var["Machine Gun Angle"], 7
            ))

    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)
        aim_target = self.target.pos.copy()

        # basic_fire_control(self, entities, level, target, wall_in)
        entity_shoot_with_startup_lag(self, og_dist, 320)

    closest_target = Fun.find_closest_in_circle(self, entities, 512, "entities")
    if closest_target:
        fortress_move_toward_point(self, closest_target, 40 * 7)
        fortress_move_away_point(self, closest_target, 25 * 7)
        if self.free_var["Run people over"] <= 0:
            self.free_var["Run people over"] = 250
            self.input["Dash"] = True
        else:
            self.free_var["Run people over"] -=1

    entity_shoot_startup_handler(self)
    # Stunned status manager
    # Fun.stunned_manager(self)
    return target, target_angle


def hover_tank_act(self, entities, level):
    angle = self.free_var["Move angle"] + 226 - 180
    pos = [self.pos[0], self.pos[1] - 16]
    pos = Fun.move_with_vel_angle(pos, 22.6274, angle)
    pos = Fun.move_with_vel_angle(pos, 20, self.aim_angle)
    # |Movement Input|----------------------------------------------------------------------------------------------
    self.running = False
    self.walking = False

    max_vel = self.vel_max

    # Handle double speed and slowness status
    if self.status["Slowness"]:
        max_vel *= 0.5
    if self.status["Double speed"]:
        max_vel *= 2

    # Checks for which direction the player must move
    # Rework it so that you are not faster when walking in diagonal, this should be fixed now
    if self.dash_cooldown <= 0:
        allow_correction = False
        speed = 0
        if self.input["Up"]:
            speed = 1
            allow_correction = True
        if self.input["Down"]:
            speed = -1
            allow_correction = True
        if self.input["Left"]:
            self.free_var["Move angle"] -= 3
            self.aim_angle -= 3
        if self.input["Right"]:
            self.free_var["Move angle"] += 3
            self.aim_angle += 3
        self.vel = Fun.move_with_vel_angle(self.vel, self.speed * speed, self.free_var["Move angle"])

        if not Fun.check_point_in_circle(max_vel, 0, 0, self.vel[0], self.vel[1]) and allow_correction:
            self.vel = Fun.move_with_vel_angle([0, 0], max_vel * speed, self.free_var["Move angle"])
        self.walking = allow_correction

        self.free_var["Move angle"] = Fun.angle_value_limiter(self.free_var["Move angle"])
        self.aim_angle = Fun.angle_value_limiter(self.aim_angle)

    self.standing_still = False
    if self.vel == [0, 0]:
        self.standing_still = True
    elif self.cutscene_mode:
        # This makes entities use their walking animation during cutscenes
        self.walking = True

    # Dash mechanic
    if self.dash_cooldown <= 0 and not self.standing_still and self.input["Dash"]:
        # Handle dash here
        Fun.play_sound("Player dash", modified_volume=0.25)
        dash_angle = self.free_var["Move angle"]
        self.dash_cooldown = self.dash_charge_time
        if self.status["Dash recovery up"] > 0:
            self.dash_cooldown //= 2
        self.vel = Fun.move_with_vel_angle(self.vel, self.dash_speed / self.friction * speed, dash_angle)
        for x in range(4):
            angle = dash_angle - 15 - 3.25 * 2 + x * 7.5 * 2
            entities["particles"].append(
                Fun.RandomParticle2(
                    Fun.move_with_vel_angle([self.pos[0], self.pos[1]], -4, angle),
                    Fun.WHITE, 1.5 + random.uniform(0, 2), 24, angle))

        if self.status["No damage"] < self.dash_iframes:
            self.status["No damage"] += self.dash_iframes
    self.dash_cooldown -= 1

    # |GunPlay|-----------------------------------------------------------------------------------------------------
    # angle, drawing_pos, length = self.aim_angle, pos, self.weapon.range + 20
    # Draw the lines
    # entities["background particles"].append(Fun.LineParticle(drawing_pos, Fun.RED, 1, length, angle, 1, 0))

    # entities["UI particles"].append(Fun.AimPoint(self.mouse_pos))
    self.weapon.passive(self, entities, level)
    if self.free_var["Grenade Shakedown"] > 0:

        if self.time % 3 == 0 and self.free_var["Allow machine gun"]:
            if self.time % 6 == 0:
                Fun.play_sound("Small arms")
                if random.random() < 0.15:
                    self.vel = Fun.move_with_vel_angle(self.vel, 7, self.free_var["Move angle"] + 45 * [1, -1][
                        round(random.random())])
            Bullets.spawn_bullet(self, entities, Bullets.Bullet, [self.pos[0], self.pos[1]-18],
                                 self.free_var["Machine Gun Angle"] + random.uniform(-self.weapon.accuracy,
                                                                 self.weapon.accuracy) + random.uniform(
                                     -self.weapon.spread, self.weapon.spread), [7, 40, 2.25, 4, {"Piercing": False, "Smoke": False}])
        if self.no_shoot_state == 0:
            # Reset variables
            self.reloading = False

            if self.input["Alt fire"]:
                self.weapon.alt_fire(self, entities, level)

            # |Main fire|-----------------------------------------------------------------------------------------------
            if self.input["Shoot"]:
                if self.weapon.ammo != 0 and self.shot_allowed:
                    # |Main fire|-------------------------------------------------------------------------------------------
                    self.shoot_bullet(entities, level)
                    # tell if the trigger was pressed
                    if not self.weapon.full_auto:
                        self.shot_allowed = False
                # if the trigger is not pressed and the weapon is not a full auto, allow to shoot for the next trigger press
                elif self.weapon.ammo == 0 and self.shot_allowed:
                    Fun.play_sound(self.weapon.jamming_sound, "SFX")
                    self.shot_allowed = False
            else:
                self.shot_allowed = True

            # |Reload|--------------------------------------------------------------------------------------------------
            if self.input["Reload"] and self.weapon.ammo_pool > 0:
                self.no_shoot_state, self.reloading = self.weapon.reload()
        else:
            self.no_shoot_state -= 1
        self.free_var["Grenade Shakedown"] -= 1
        self.free_var["Grenade Shakedown angle"] = [self.free_var["Move angle"], self.aim_angle]
        p = self.aim_angle
        self.aim_angle = Fun.angle_value_limiter(Fun.move_angle(self.angle, self.aim_angle, self.weapon.handle))
        if round(p) != round(self.aim_angle) and self.time % 12 == 0:
            Fun.play_sound("Chain click")
    elif self.free_var["Grenade Shakedown"] > -180:
        self.free_var["Grenade Shakedown"] -= 1
        angle = self.free_var["Grenade Shakedown"] * 6 + self.free_var["Grenade Shakedown angle"][0]
        self.free_var["Move angle"] = angle
        self.aim_angle = self.free_var["Grenade Shakedown angle"][1] + self.free_var["Grenade Shakedown"] * 6
        if self.free_var["Grenade Shakedown"] % 2 == 0 and self.free_var["Grenade Shakedown"] < 60:
            Bullets.spawn_bullet(
                self, entities, Bullets.BulletSlowing,
                Fun.move_with_vel_angle(self.pos, 32, self.aim_angle),
                self.aim_angle + random.uniform(-8, 8),
                [5 + 5 * random.random(), 320, 7, 8, {"Piercing": False, "Smoke": False, "Colour": (107, 165, 153),
                                                      "Slowdown rate": random.random() / 3}])

        if abs(self.free_var["Grenade Shakedown"]) % 8 == 0:
            Bullets.spawn_bullet(
                self, entities, Bullets.GrenadeType1,
                Fun.move_with_vel_angle(self.pos, 32, angle),
                angle,
                [4, 200, 4, 20, {"Secondary explosion": {"Duration": 10, "Growth": 4,
                                                        "Damage mod": 0}}])
            if abs(self.free_var["Grenade Shakedown"]) % 16 == 0:
                Fun.play_sound("Betel 2")
        # Shoot grenades
    else:
        self.free_var["Grenade Shakedown"] = 800

    # |Status effects|----------------------------------------------------------------------------------------------
    # ha ha, Fun go brr
    Fun.status_manager(self, entities)

    # |Movement Output|---------------------------------------------------------------------------------------------
    # Make the player move
    Fun.movement_output(self, level)
    damage = round(abs(self.vel[0]) + abs(self.vel[1])) * 2
    if damage > 40:
        damage = 40
    for e in entities["entities"]:
        if e == self: continue
        if self.collision_box.colliderect(e.collision_box):
            e.vel = Fun.move_with_vel_angle(e.vel, 2, Fun.angle_between(e.collision_box.center, self.pos))
            if e.team != self.team:
                Fun.damage_calculation(e, damage, "Melee", death_message="Ran over")
            pass
    if self.draw_aim_line or self.weapon.laser_sight:
        entities["background particles"].append(Fun.LineParticle(
            Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), Fun.BLUE, 1, self.weapon.range-20, self.aim_angle, 2, 0))


def hover_tank_draw(self, WIN, scrolling):
    h_mod = 0.75
    Fun.draw_spritestack(WIN, Fun.SPRITE_HOVER_TANK_CHASSIS, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                         self.free_var["Move angle"] + 90, height_diff=h_mod)
    Fun.draw_spritestack(WIN, Fun.SPRITE_HOVER_TANK_TURRET, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1] - 17 * h_mod],
                         self.aim_angle + 90, height_diff=h_mod)
    Fun.draw_spritestack(WIN, Fun.SPRITE_HOVER_TANK_GUN, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1] - 24 * h_mod],
                         self.free_var["Machine Gun Angle"] + 90, height_diff=h_mod)


def attack_helicopter_input(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    # Find machine gun angle
    p_targets = {}
    for e in entities["entities"]:
        if e.team == self.team:
            continue
        if e.agro >= 0 and e.status["Stealth"] == 0:
            key = f"{e.agro}"
            if key not in p_targets:
                p_targets.update({key: [e]})
            else:
                p_targets[key].append(e)
    keys = list(p_targets.keys())
    keys.sort()
    self.free_var["Allow machine gun"] = False
    if p_targets:
        mod = -2
        if len(keys) == 1:
            mod = -1
        aaa = keys[mod]
        mg_target = p_targets[aaa][0]
        mg_target = mg_target.pos
        self.free_var["Allow machine gun"] = Fun.distance_between(mg_target, [self.pos[0], self.pos[1]-18]) < 40 * 7
        self.free_var["Machine Gun Angle"] = Fun.angle_value_limiter(
            Fun.move_angle(
                Fun.angle_between(mg_target, [self.pos[0], self.pos[1]-18]), self.free_var["Machine Gun Angle"], 7
            ))

    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)
        aim_target = self.target.pos.copy()

        # # basic_fire_control(self, entities, level, target, wall_in)
        entity_shoot_with_startup_lag(self, og_dist, 320)

    closest_target = Fun.find_closest_in_circle(self, entities, 512+128, "entities")
    if closest_target:
        fortress_move_toward_point(self, closest_target, 40 * (2 + 5 * math.sin(self.time/30)))
        fortress_move_away_point(self, closest_target, 35 * 2)
        if self.free_var["Run people over"] <= 0:
            self.free_var["Run people over"] = 250
            self.input["Dash"] = True
        else:
            self.free_var["Run people over"] -=1

    entity_shoot_startup_handler(self)
    # Stunned status manager
    # Fun.stunned_manager(self)
    return target, target_angle


def attack_helicopter_act(self, entities, level):
    # pos = Fun.move_with_vel_angle(pos, 22.6274, angle)
    # pos = Fun.move_with_vel_angle(pos, 20, self.aim_angle)
    # |Movement Input|----------------------------------------------------------------------------------------------
    self.running = False
    self.walking = False

    max_vel = self.vel_max

    # Handle double speed and slowness status
    # if self.status["Slowness"]:
    #     max_vel *= 0.5
    # if self.status["Double speed"]:
    #     max_vel *= 2

    # Checks for which direction the player must move
    # Rework it so that you are not faster when walking in diagonal, this should be fixed now
    if self.dash_cooldown <= 0:
        allow_correction = False
        speed = 0
        if self.input["Up"]:
            speed = 1
            allow_correction = True
        if self.input["Down"]:
            speed = -1
            allow_correction = True
        if self.input["Left"]:
            self.free_var["Move angle"] -= 3
            self.aim_angle -= 3
        if self.input["Right"]:
            self.free_var["Move angle"] += 3
            self.aim_angle += 3
        self.free_var["Move angle"] = self.angle
        self.aim_angle = self.angle
        self.vel = Fun.move_with_vel_angle(self.vel, self.speed * speed, self.free_var["Move angle"])

        if not Fun.check_point_in_circle(max_vel, 0, 0, self.vel[0], self.vel[1]) and allow_correction:
            self.vel = Fun.move_with_vel_angle([0, 0], max_vel * speed, self.free_var["Move angle"])
        self.walking = allow_correction

        self.free_var["Move angle"] = Fun.angle_value_limiter(self.free_var["Move angle"])
        self.aim_angle = Fun.angle_value_limiter(self.aim_angle)

    self.standing_still = False
    if self.vel == [0, 0]:
        self.standing_still = True
    elif self.cutscene_mode:
        # This makes entities use their walking animation during cutscenes
        self.walking = True

    # |GunPlay|-----------------------------------------------------------------------------------------------------
    # angle, drawing_pos, length = self.aim_angle, pos, self.weapon.range + 20
    # Draw the lines
    # entities["background particles"].append(Fun.LineParticle(drawing_pos, Fun.RED, 1, length, angle, 1, 0))

    self.weapon.passive(self, entities, level)
    if self.time % 2 == 0 and self.free_var["Allow machine gun"]:
        if self.time % 4 == 0:
            Fun.play_sound("Small arms")
        angle = self.aim_angle + 16 * math.sin(self.time / 2)
        Bullets.spawn_bullet(self, entities, Bullets.Bullet,
                             Fun.move_with_vel_angle([self.pos[0], self.pos[1] - 6], 56, angle),
                             angle, [7, 70, 2.25, 4, {"Piercing": False, "Smoke": False}])
    if self.no_shoot_state == 0:
        # Reset variables
        self.reloading = False
        if self.input["Alt fire"]:
            self.weapon.alt_fire(self, entities, level)

        # |Main fire|-----------------------------------------------------------------------------------------------
        if self.input["Shoot"]:
            if self.weapon.ammo != 0 and self.shot_allowed:
                # |Main fire|-------------------------------------------------------------------------------------------
                # self.shoot_bullet(entities, level)
                # Fires rockets (HE, Incendiary, Grapeshot)
                m_type = random.random()
                b_info = [5, 160, 4, 80, {"Targeting range": 300,
                                          "Targeting angle": 5,
                                          "Manoeuvrability": 2,
                                          "Target": "enemies",
                                          "Secondary explosion": {"Duration": 10,
                                                                  "Growth": 6,
                                                                  "Damage mod": 1}}]
                b_class = Bullets.Missile
                if m_type < 0.33:
                    b_info[4]["Secondary explosion"] = {
                        "Amount of Bullets": 16,
                        "Bullet Info": [5, 90, 4, 5,
                                        {"Particle allowed": True, "Burn chance": 1, "Burn duration": 30,
                                         "Colour": Fun.FIRE}]
                    }
                    b_class = Bullets.MissileIncendiary
                if m_type > 0.66:
                    b_info[4]["Secondary explosion"] = {
                        "Amount of Bullets": 16,
                        "Bullet Info": [5, 90, 4, 5,
                                        {}],
                        "Angle range": 33
                    }
                    b_class = Bullets.MissileShrapnel
                for x in range(8):
                    Bullets.spawn_bullet(
                        self, entities, b_class,
                        Fun.move_with_vel_angle(self.pos, (x // 2) * 8,
                                                [-90 + self.aim_angle, 90 + self.aim_angle][x % 2]),
                        self.aim_angle + [0, 0, -7.5, 7.5, -15, 15, -22.5, 22.5][x], b_info)
                    self.slowdown_rate = 1 - random.random() * 2

                # tell if the trigger was pressed
                if not self.weapon.full_auto:
                    self.shot_allowed = False
            # if the trigger is not pressed and the weapon is not a full auto, allow to shoot for the next trigger press
            elif self.weapon.ammo == 0 and self.shot_allowed:
                Fun.play_sound(self.weapon.jamming_sound, "SFX")
                self.shot_allowed = False
        else:
            self.shot_allowed = True

        # |Reload|--------------------------------------------------------------------------------------------------
        if self.input["Reload"] and self.weapon.ammo_pool > 0:
            self.no_shoot_state, self.reloading = self.weapon.reload()
    else:
        self.no_shoot_state -= 1
    p = self.aim_angle
    self.aim_angle = Fun.angle_value_limiter(Fun.move_angle(self.angle, self.aim_angle, self.weapon.handle))
    if round(p) != round(self.aim_angle) and self.time % 12 == 0:
        Fun.play_sound("Chain click")

    # Flares
    # if self.time % 180 == 0:
    #     for b in entities["bullets"]:
    #         if b.team == self.team:
    #             continue
    #         if "Manoeuvrability" in b.og_info[4]:
    #             if b.target_pos != self.pos:
    #                 continue
    #             # Flares effect
    #             if random.random() < 0.75:
    #                 #
    #                 b.team = self.team

    # |Status effects|----------------------------------------------------------------------------------------------
    # ha ha, Fun go brr
    Fun.status_manager(self, entities)

    # |Movement Output|---------------------------------------------------------------------------------------------
    # Make the player move
    if self.status["High friction"] > 0:
        self.vel = [self.vel[0] * 0.25, self.vel[1] * 0.25]

    # This give the direction the entity moves towards,
    # when using it for anything you should check if the entity is even moving
    self.direction_angle = Fun.angle_between(self.vel, [0, 0])

    # collision_check(self, level["map"])
    # Make the guy move
    self.pos[0] += self.vel[0]
    self.pos[1] += self.vel[1]
    self.collision_box = pg.Rect(self.pos[0] - self.thiccness / 2, self.pos[1] - self.thiccness / 2,
                                 self.thiccness, self.thiccness)

    # |Friction handling|-----------------------------------------------------------------------------------------------
    friction_strength = self.friction
    if self.status["Forced Slide"]:  # Some enemies will slide
        friction_strength = 0.025
    if self.status["Low friction"] > 0:
        friction_strength = 0
    for i in range(2):
        if self.vel[i] != 0:
            if self.vel[i] >= 0 + friction_strength:
                self.vel[i] -= friction_strength
            elif self.vel[i] <= 0 - friction_strength:
                self.vel[i] += friction_strength
            else:
                self.vel[i] = 0
    #


def attack_helicopter_draw(self, WIN, scrolling):
    h_mod = 0.75
    WIN.blit(Fun.ENTITY_SHADOW_SIZE_2, Fun.move_with_vel_angle(
        (self.pos[0] - 32 + scrolling[0], self.pos[1] + 11 + scrolling[1]), 20, self.aim_angle),
        special_flags=pg.BLEND_RGBA_SUB)

    Fun.draw_spritestack(WIN, Fun.SPRITE_ATTACK_HELICOPTER, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                         self.aim_angle + 90, height_diff=h_mod)

    Fun.draw_spritestack(WIN, Fun.SPRITE_ATTACK_HELICOPTER_BLADE, Fun.move_with_vel_angle(
        [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1] - 37 * h_mod], 20, self.aim_angle),
                         self.time * 13.5, height_diff=h_mod)


ACT_FREELY_DICT = {
         "Lord": ally_sub_input_roam,
         "Emperor": ally_sub_input_focus_objective,
         "Wizard": ally_sub_input_wizard,
         "Sovereign": ally_sub_input_sniper,
         "Duke": ally_sub_input_duke,
         "Jester": ally_sub_input_jester,
         "Condor": ally_sub_input_condor,

         "Curtis": ally_sub_input_focus_objective,
         "Doppelgänger": ally_sub_input_focus_objective,
         "Lawrence": ally_sub_input_lawrence,
         "Mark": ally_sub_input_sniper,
         "Vivianne": ally_sub_input_wizard
     }
# |Repertories|---------------------------------------------------------------------------------------------------------
# Entity stats
H_LO, H_LM, H_MO, H_MH, H_HO = 60, 90, 130, 170, 200        # Max Health
A_LO, A_LM, A_MO, A_MH, A_HO = 40, 60, 90, 120, 140         # Max Armour
V_LO, V_LM, V_MO, V_MH, V_HO = 2, 3, 4, 5, 5.75             # Max Speed
R_LO, R_LM, R_MO, R_MH, R_HO = 256, 384, 512, 640, 768      # Vision range
D_LO, D_LM, D_MO, D_MH, D_HO = 15, 30, 45, 60, 75           # Targeting angle
S_LO, S_LM, S_MO, S_MH, S_HO = 1, 0.85, 0.65, 0.55, 0.45    # Stealth mod
C_LO, C_LM, C_MO, C_MH, C_HO = 1, 2, 4, 6, 10               # Stealth Counter
T_LO, T_LM, T_MO, T_MH, T_HO = 8, 12, 16, 24, 32            # Size, thickness

# Dash speed
DS_LO, DS_LM, DS_MO, DS_MH, DS_HO = 9, 11, 13, 15, 17
DI_LO, DI_LM, DI_MO, DI_MH, DI_HO = 0, 0, 0, 0, 0
DR_LO, DR_LM, DR_MO, DR_MH, DR_HO = 0, 0, 0, 0, 0

# Driving
DRIVE_LO, DRIVE_LM, DRIVE_MO, DRIVE_MH, DRIVE_HO = 0, 1, 2, 3, 4
NO_RESIT = {"Physical": 1,  "Fire": 1,    "Explosion": 1,  "Energy": 1,       "Melee": 1, "Healing": 0}   # M/H
# Resistances M Average 0.85
LO_RESIT = {"Physical": 0.7,  "Fire": 1,    "Explosion": 0.7,  "Energy": 1,       "Melee": 1, "Healing": -1}   # M/H
EM_RESIT = {"Physical": 1,    "Fire": 0.8,  "Explosion": 0.8,  "Energy": 0.8,     "Melee": 1, "Healing": -1}   # M
WI_RESIT = {"Physical": 0.95, "Fire": 0.7,  "Explosion": 0.75, "Energy": 0.8,     "Melee": 1, "Healing": -1}   # M/H
SO_RESIT = {"Physical": 1,    "Fire": 1,    "Explosion": 1,    "Energy": 1,       "Melee": 1, "Healing": -1}   # L
DU_RESIT = {"Physical": 0.7,  "Fire": 1,    "Explosion": 1,    "Energy": 0.7,     "Melee": 1, "Healing": -1}   # M
JE_RESIT = {"Physical": 0.5,  "Fire": 0.4,  "Explosion": 0.7,  "Energy": 0.4,     "Melee": 1, "Healing": 0}    # H
CO_RESIT = {"Physical": 0.6,  "Fire": 0.9,  "Explosion": 0.8,  "Energy": 0.6,     "Melee": 1, "Healing": -1}   # M/H
FO_RESIT = {"Physical": 0.6,  "Fire": 0.2,  "Explosion": 0.6,  "Energy": 0.3,     "Melee": 1, "Healing": 0}   # M/H

CU_RESIT = {"Physical": 0.75, "Fire": 0.85, "Explosion": 0.9,  "Energy": 0.9,     "Melee": 1, "Healing": -1}   # M
LA_RESIT = {"Physical": 0.8,  "Fire": 0.8,  "Explosion": 0.9,  "Energy": 0.9,     "Melee": 1, "Healing": -1}   # M
MA_RESIT = {"Physical": 0.9,  "Fire": 0.8,  "Explosion": 0.9,  "Energy": 0.8,     "Melee": 1, "Healing": -1}   # M
VI_RESIT = {"Physical": 0.9,  "Fire": 0.9,  "Explosion": 0.8,  "Energy": 0.8,     "Melee": 1, "Healing": -1}   # M

# HEALING_PRIORITY_LIST = {"Wizard": -1, "Emperor": 0, "Lord": 1, "Duke": 2, "Condor": 3, "Jester": 4, "Sovereign": 5}
player_repertory = {
    # THR-1
    #               MHlt    MArm    Resits  Spd     VisRg   SltMod  SltCntr Size    Driving DshSpd  DshInv  DshReco
    # Lord	        M/H     M       M/H     M       M/H     L--     L/M     M/H     M       H       L/M     M       Generates tons of agro, all weapons do AoE damage
    "Lord": {
        "name": "Lord",
        "health": H_MH, "armour": A_MO, "damage resistances": LO_RESIT,
        "sprites": "Sprites/Player/THR-1/Lord.png",

        "thickness": T_MH, "vel max": V_MO, "speed": 2.2, "friction": 1.5,
        "dash": {"speed": DS_HO, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "Saloum Mk-2", "skills": ["Gauntlet Punch", "Beast Mode"],
        # AI
        "func input": test_ally_input, "func act": player_act, "func draw": player_draw, "on death": lord_on_death,
        "targeting range": R_MH, "targeting angle": D_LM, "wall hack": False,
        "driving": DRIVE_MO,
        "free var": {"Ally waypoint": [0, 0]}
    },
    # Emperor	    M       L/M     M       M/H     H       M       M/H     M       M       M       H       H       Jack of all trades
    "Emperor": {
        "name": "Emperor",
        "health": H_MO, "armour": A_LM, "damage resistances": EM_RESIT, "sprites": "Sprites/Player/THR-1/Emperor.png",
        "thickness": T_MO,
        "vel max": V_MH,
        "speed": 2.2,
        "friction": 1.5,
        "dash": {"speed": DS_MO, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "GunBlade", "skills": ["Stun Kick", "Mega Buff" ],
        # AI
        "func input": test_ally_input, "func act": player_act, "func draw": player_draw, "on death": "none",
        "targeting range": R_HO, "targeting angle": D_MO, "stealth mod": S_MO, "stealth counter": C_MH,
        "wall hack": False,
        "driving": DRIVE_MO,
        "free var": {"Ally waypoint": [0, 0], "Startup lag": 0, "Startup time": 60, "Kicked": 0}
    },
    # Wizard        L/M     M       M/H     M       M       L/M     M       M       H       M       H       M       Area denial
    "Wizard": {
        "name": "Wizard",
        "health": H_LM, "armour": A_MO, "damage resistances": WI_RESIT, "sprites": "Sprites/Player/THR-1/Wizard.png",
        "thickness": T_MO,
        "vel max": V_MO, "speed": 2.2, "friction": 1.5,
        "dash": {"speed": DS_MO, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "Jeanne's Family Shotgun", "skills": ["Building", "All Guns Blazing"],
        # AI
        "func input": test_ally_input, "func act": player_act, "func draw": player_draw, "on death": "none",
        "targeting range": R_MO, "targeting angle": D_MH, "stealth mod": S_LM, "stealth counter": C_MO,
        "wall hack": False,
        "driving": DRIVE_HO,
        "free var": {"Ally waypoint": [0, 0]}
    },
    # Sovreig       L/M     L/M     L       M/H     H++     M/H     H       L       L       L/M     L       M       Sniper recon
    "Sovereign": {
        "name": "Sovereign",
        "health": H_LM, "armour": A_LM, "damage resistances": SO_RESIT, "sprites": "Sprites/Player/THR-1/Sovereign.png",
        "thickness": T_LO,
        "vel max": V_MH,
        "speed": 2.2,
        "friction": 1.5,
        "dash": {"speed": DS_LM, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "St-Maurice", "skills": ["Cardboard box", "Detect Targets"],
        # AI
        "func input": test_ally_input, "func act": player_act, "func draw": player_draw, "on death": "none",
        "targeting range": R_HO * 1.5, "targeting angle": D_LM, "stealth mod": S_MH, "stealth counter": C_HO,
        "wall hack": False,
        "driving": DRIVE_LO,
        "free var": {"Ally waypoint": [0, 0], "Detect Targets Duration": 3 * 60, "Exposed blue ball timer": 0}
    },
    # Duke	        M       L/M     M       H       M       H       M       L/M     L/M     H       H       H	    Plays with agro
    "Duke": {
        "name": "Duke",
        "health": H_MO, "armour": A_LM, "damage resistances": DU_RESIT,
        "sprites": "Sprites/Player/THR-1/Duke.png",
        "thickness": T_LM,
        "vel max": V_HO,
        "speed": 2.2,
        "friction": 1.5,
        "dash": {"speed": DS_HO, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "Chain Axe", "skills": ["Tail Swipe", "Smoke Screen"],
        # AI
        "func input": test_ally_input, "func act": player_act, "func draw": player_draw, "on death": "none",
        "targeting range": R_MO, "targeting angle": D_HO, "stealth mod": S_HO, "stealth counter": C_HO,
        "driving": DRIVE_LM,
        "wall hack": False,
        "free var": {"Ally waypoint": [0, 0]}
    },
    # Jester	    L--     H++     H       L       L/M     L/M     H++     M/H     L/M     L--     H++     L       Primary support. Helps them not dying
    "Jester": {
        "name": "Jester",
        "health": int(H_LO * 0.5), "armour": A_MH * 2, "damage resistances": JE_RESIT,
        "sprites": "Sprites/Player/THR-1/Jester.png",
        "thickness": T_MH,
        "vel max": V_LO,
        "speed": 2.2,
        "friction": 0.5,
        "dash": {"speed": DS_LO * 0.4, "i-frames": 12, "charge": 35},

        # Weapons
        "weapon": "Epicurean Medic Rifle", "skills": ["Discharge", "Robot Fuck Off"],
        # AI
        "func input": jester_input, "func act": player_act, "func draw": player_draw, "on death": "none",
        "targeting range": R_LM, "targeting angle": D_MH, "stealth mod": S_LM, "stealth counter": C_HO * 1.2,
        "wall hack": False,
        "driving": DRIVE_LM,
        "free var": {"Ally waypoint": [0, 0]}
    },
    # Condor        H       H       M/H     L/M     M       L       L/M     M/H     M/H     M       L       L       Tank and cause debuffs
    "Condor": {
        "name": "Condor",
        "health": H_HO, "armour": A_HO, "damage resistances": CO_RESIT,
        "sprites": "Sprites/Player/THR-1/Condor.png",

        "thickness": T_MH,
        "vel max": V_LM,
        "speed": 2.2,
        "friction": 0.8,
        "dash": {"speed": DS_LO, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "Type 41 SMG", "skills": ["Armour Breaker", "Last Stand"],
        # AI
        "func input": test_ally_input, "func act": player_act, "func draw": player_draw, "on death": "condor_on_death",
        "targeting range": R_MO, "targeting angle": D_MO, "stealth mod": S_LO, "stealth counter": C_LM,
        "driving": DRIVE_MH,
        "wall hack": False,
        "free var": {"Ally waypoint": [0, 0]}
    },

    # Fortress APC
    "Fortress": {
        "name": "Fortress",
        "health": H_HO * 3, "armour": A_HO *  3, "damage resistances": FO_RESIT,
        "sprites": "Sprites/Player/THR-1/Condor.png",

        "thickness": 60,
        "vel max": V_MO,
        "speed": 2.2,
        "friction": 0.8,
        "dash": {"speed": DS_HO, "i-frames": 0, "charge": 35},
        # Weapons
        "weapon": "Fortress Machine Gun", "skills": ["Mortar", "Repairs"],
        # AI
        "func input": "fortress_input", "func act": "fortress_act", "func draw": "fortress_draw", "on death": "fortress_on_death",
        "targeting range": R_MO, "targeting angle": 180, "stealth mod": S_LO, "stealth counter": C_LM,
        "wall hack": False,
        "driving": DRIVE_HO,
        "free var": {"Ally waypoint": [0, 0], "Move angle": 0, "IS AN APC": "Fortress"}
    },

    # Zoar Colonists
    #               MHlt    MArm    Resits  Spd     VisRg   SltMod  SltCntr Size    Driving DshSpd  DshInv  DshReco
    # Curtis        M       M       M       H++     H       M/H     M       M       L       H++     H++     H++     Great at fighting. Pressing reload with a gun that can't be reloaded switch the gun
    "Curtis": {
        "name": "Curtis",
        "wall hack": False,
        "targeting angle": 90, "targeting range": 512,
        "health": 200,
        "armour": 50,
        "damage resistances": CU_RESIT,
        "weapon": "Standard Shotgun",
        # "weapon": "War and Peace",

        "thickness": 16,
        "vel max": 6.25,
        "speed": 1.17,
        "friction": 1.15,
        "dash": {"speed": DS_HO, "i-frames": 24, "charge": 25},

        "sprites": "Sprites/Player/Curtis.png",

        "skills": ["Kick", "Le Mat"],
        "func input": test_ally_input,
        "func act": player_act,
        "func draw": player_draw,
        "on death": none,
        "free var": {"Ally waypoint": [0, 0]}
    },
    # Law.	        H       H       M       H       M       H       M       M       L       M/H     M/H     M/H     AoE attacks
    "Lawrence": {
        "name": "Lawrence",
        "health": 350,
        "armour": 75,
        "damage resistances": LA_RESIT,
        "sprites": "Sprites/Player/Lawrence.png",

        "thickness": 20,
        "vel max": 5.25,
        "speed": 1.5,
        "friction": 1.25,
        "dash": {"speed": 16, "i-frames": 24, "charge": 25},

        # Weapons
        # "weapon": "Lawrence's handgun",
        "weapon": "Lawrence's Cutlass & Flintlock",
        # Skills
        "skills": ["Flame Canyon", "Flame Burst"],
        # AI
        "func input": test_ally_input,
        "func act": player_act,
        "func draw": player_draw,
        "on death": "none",
        "targeting range": 750,
        "targeting angle": 33,
        "wall hack": False,
        "free var": {"Ally waypoint": [0, 0], "Aim time": 0, "Startup lag": 0, "Startup time": 60},
    },
    # Mark          M       L/M     M       M       H++     H       H++     M       H       M       M       M	Sniper, causes debuffs on his targets
    "Mark": {
        "name": "Mark",
        "health": 250,
        "armour": 50,
        "damage resistances": MA_RESIT,
        "sprites": "Sprites/Player/Mark.png",

        # Speed stuff
        "thickness": 16,
        "vel max": 3,
        "speed": 1.3,
        "friction": 1,
        "dash": {"speed": 9, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "Mark's Rifle", "skills": ["Target Locator", "Smoke Grenade"],
        # AI
        "func input": test_ally_input,
        "func act": player_act,
        "func draw": player_draw,
        "on death": "none",
        "targeting range": 750,
        "targeting angle": 33,
        "wall hack": False,
        "free var": {"Ally waypoint": [0, 0]}
    },
    # Viv.          L/M     M       M       M       M       M       M/H     M       H       M       M       M       Primary support. Make weapons work better
    "Vivianne": {
        "name": "Vivianne",
        "health": 250,
        "armour": 50,
        "damage resistances": VI_RESIT,
        "sprites": "Sprites/Player/Vivianne.png",

        "thickness": 15,
        "vel max": 4.4,
        "speed": 2.2,
        "friction": 1.5,
        "dash": {"speed": 8, "i-frames": 12, "charge": 35},

        # Weapons
        "weapon": "Vivianne's Rifle",
        "skills": ["Rat Shot", "Reaper Rounds"],
        # AI
        "func input": test_ally_input,
        "func act": player_act,
        "func draw": player_draw,
        "on death": "none",
        "targeting range": 750,
        "targeting angle": 33,
        "wall hack": False,
        "free var": {"Ally waypoint": [0, 0], "Summon cooldown time": 360, "Summon cooldown": 0, "Summon limit": 1,
                     "Summon pool": [], "Active summons": []}
    },

    "Sand Buggy": {
        "name": "Sand Buggy",
        "health": H_HO * 2, "armour": A_HO * 2, "damage resistances": FO_RESIT,
        "sprites": "Sprites/Player/THR-1/Condor.png",

        "thickness": 60,
        "vel max": V_HO,
        "speed": 0.9,
        "friction": 0.65,
        "dash": {"speed": DS_LO, "i-frames": 0, "charge": 15},
        # Weapons
        "weapon": "Buggy Gun", "skills": ["Drift", "Rocket Burst"],
        # AI
        "func input": "fortress_input", "func act": "buggy_act", "func draw": "buggy_draw",
        "on death": "fortress_on_death",
        "targeting range": R_MH, "targeting angle": 180, "stealth mod": S_LM, "stealth counter": C_MH,
        "wall hack": False,
        "driving": DRIVE_HO,
        "free var": {"Ally waypoint": [0, 0], "Move angle": 0, "Target Move angle": 0, "Move vel": 0, "IS AN APC": "Sand Buggy"}
    },
}

# Resistances   set to 1 mean no resistance
F1_RESIT_L = {"Physical": 1,    "Fire": 1,    "Explosion": 1,    "Energy": 0.80,    "Melee": 1,     "Healing": 0}
F1_RESIT_M = {"Physical": 0.80, "Fire": 1,    "Explosion": 1,    "Energy": 0.60,    "Melee": 1,     "Healing": 0}
F1_RESIT_H = {"Physical": 0.66, "Fire": 0.75, "Explosion": 1,    "Energy": 0.25,    "Melee": 1,     "Healing": 0}

F2_RESIT_L = {"Physical": 1,    "Fire": 1,    "Explosion": 1,    "Energy": 1,       "Melee": 1,     "Healing": 0}
F2_RESIT_M = {"Physical": 1,    "Fire": 1,    "Explosion": 1,    "Energy": 1,       "Melee": 1,     "Healing": 0}
F2_RESIT_H = {"Physical": 1,    "Fire": 1,    "Explosion": 1,    "Energy": 1,       "Melee": 1,     "Healing": 0}

F3_RESIT_L = {"Physical": 1,    "Fire": 1,    "Explosion": 0.66, "Energy": 1,       "Melee": 1,     "Healing": 0}
F3_RESIT_M = {"Physical": 0.75, "Fire": 1,    "Explosion": 0.5,  "Energy": 1,       "Melee": 1,     "Healing": 0}
F3_RESIT_H = {"Physical": 0.5,  "Fire": 0.25, "Explosion": 0.33, "Energy": 0.4,     "Melee": 1,     "Healing": 0}
# 410 of health           820           1640               1242            1025
NO_RESIT_L = {"Physical": 1,    "Fire": 1,    "Explosion": 1,    "Energy": 1,       "Melee": 1,     "Healing": 0}

enemy_repertory = {
    #                   MHlt	MArm	Resits	Spd 	VisRg	SltMod	SltCntr	Size
    # |Circle|----------------------------------------------------------------------------------------------------------
    # Manager
    "Manager":
        {"name": "Manager",
         "faction": "FAC-1",
         "type": "Grunt",
         "targeting range": R_MH, "targeting angle": 25, "stealth mod": S_MH, "stealth counter": C_LM,
         "wall hack": False,
         "health": H_MO, "armour": A_LO, "damage resistances": F1_RESIT_L,
         "thickness": T_MO,
         "vel max": V_MO,
         "speed": 1.5,
         "friction": 1.5,
         "weapon": "Laser Carbine",

         "func input": "enemy_input_faction_1_body_guard",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_sniper",
         "sprites": "Sprites/Enemies/Manager.png",
         "on death": "none",
         "free var": {"Startup lag": 0, "Startup time": 50, "Is VIP": True}
         },
    # BodyGuard	        M	    L	    L       M	    M/H	    L/M	    M	    M	    Escorts Heavy Sniper
    "Body Guard":
        {"name": "Body Guard",
         "faction": "FAC-1",
         "type": "Grunt",
         "targeting range": R_MH, "targeting angle": 25, "stealth mod": S_MH, "stealth counter": C_LM,
         "wall hack": False,
         "health": H_MO, "armour": A_LO, "damage resistances": F1_RESIT_L,
         "thickness": T_MO,
         "vel max": V_MO,
         "speed": 1.5,
         "friction": 1.5,
         "weapon": "Laser Rifle",

         "func input": "enemy_input_faction_1_body_guard",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_sniper",
         "sprites": "Sprites/Enemies/Body Guard.png",
         "on death": "none",
         "free var": {"Startup lag": 0, "Startup time": 60}
         },
    # Heavy Sniper      M	    M	    M	    L/M	    H	    L	    M	    M/H	    Main damage source
    "Heavy Sniper":
        {"name": "Heavy Sniper",
              "faction": "FAC-1",
              "type": "Shock",
              "targeting range": R_HO, "targeting angle": 25, "stealth mod": S_LO, "stealth counter": C_MO,
              "wall hack": False,
              "health": H_MO, "armour": A_MO, "damage resistances": F1_RESIT_M,
              "thickness": T_MH,
              "vel max": V_LM,
              "speed": 1.5,
              "friction": 1.5,
              "weapon": "Heavy Laser",

              "func input": "enemy_input_faction_1_heavy_sniper",
              "func act": "enemy_act_type_1",
              "func draw": "enemy_draw_sniper",
              "sprites": "Sprites/Enemies/Heavy Sniper.png",
              "on death": "none",
              "free var": {"Startup lag": 0, "Startup time": 120, "aim line colour": [1, 2]}
              },
    # Radar Operator    L/M	    L/M	    L	    M/H	    H++	    L	    L	    M	    Share detected target for MsslOp
    "Radar Operator":
        {"name": "Radar Operator",
         "faction": "FAC-1",
         "type": "Support",
         "targeting range": R_HO * 1.2, "targeting angle": 25, "stealth mod": S_LO, "stealth counter": C_LO,
         "wall hack": False,
         "health": H_LM, "armour": A_LM, "damage resistances": F1_RESIT_L,
         "thickness": T_MO,
         "vel max": V_MH,
         "speed": 1.5,
         "friction": 1.5,
         "weapon": "Radar",

         "func input": "enemy_input_faction_1_radar",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Radar Operator.png",
         "on death": "none",
         "free var": {}
         },
    # Missile Operator  M	    M	    M	    L/M	    M	    L	    L/M	    M	    Uses missiles
    "Missile Operator":
        {"name": "Radio Operator",
         "faction": "FAC-1",
         "type": "Specialist",
         "targeting range": R_MO, "targeting angle": 60,  "stealth mod": S_LO, "stealth counter": C_LM,
         "wall hack": False,
         "health": H_MO, "armour": A_MO, "damage resistances": F1_RESIT_M,
         "thickness": T_MO,
         "vel max": V_LM,
         "speed": 1.5,
         "friction": 1.5,
         "weapon": "Missile Pod",

         "func input": "enemy_input_faction_1_missile",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Missile Operator.png",
         "on death": "none",
         "free var": {"missile target": False}
         },
    # Marksman	        M	    M	    L	    M	    M/H	    M	    H	    M	    Mark players. Marked players' location is always known
    "Marksman":
        {"name": "Marksman",
         "faction": "FAC-1",
         "type": "Specialist 2",
         "targeting range": R_HO, "targeting angle": 25, "stealth mod": S_MO, "stealth counter": C_HO,
         "wall hack": False,
         "health": H_MO, "armour": A_MO, "damage resistances": F1_RESIT_L,
         "thickness": T_MO,
         "vel max": V_MO,
         "speed": 1.5,
         "friction": 1.5,
         "weapon": "Marker Laser",

         "func input": "enemy_input_faction_1_basic",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_sniper",
         "sprites": "Sprites/Enemies/Marksman.png",
         "on death": "none",
         "free var": {"Startup lag": 0, "Startup time": 90, "aim line colour": [2]}
         },
    # Enforcer	        H	    M/H	    H	    L	    M/H	    L--	    M	    H	    Multiple attacks for all ranges
    "Enforcer":
        {"name": "Enforcer",
         "faction": "FAC-1",
         "type": "Elite",
         "targeting range": R_MH, "targeting angle": 25, "stealth mod": S_LO * 1.2, "stealth counter": C_MO,
         "wall hack": False,
         "health": H_HO, "armour": H_MH, "damage resistances": F1_RESIT_H,
         "thickness": T_HO,
         "vel max": V_LO,
         "speed": V_LO,
         "friction": V_LO,
         "weapon": "ARWS",

         "func input": "enemy_input_faction_1_basic",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_enforcer",
         "on death": "enforcer_on_death",
         "free var": {"Startup lag": 0, "Startup time": 60, "missile target": False}
         },
    #                   MHlt	MArm	Resits	Spd 	VisRg	SltMod	SltCntr	Size
    # |Triangle|--------------------------------------------------------------------------------------------------------
    "Sculptor":
        {"name": "Sculptor",
         "faction": "FAC-2",
         "type": "Grunt",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_MO, "stealth counter": C_LO,
         "wall hack": False,
         "health": H_MO, "armour": A_LM, "damage resistances": F2_RESIT_H,
         "thickness": T_LO, "vel max": V_HO, "speed": 1.5, "friction": 1.5,
         "weapon": "Plasma Spray",
         "func input": "enemy_input_faction_2_basic", "func act": "enemy_act_type_1", "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Sculptor.png", "on death": "none",
         "free var": {"Is VIP": True}
         },
    # Skirmisher	    L/M	    L--	    M       M/H	    M	    H       M/H	    L/M	    No armour, low range. FAST. Dodges to stay alive
    "Skirmisher":
        {"name": "Skirmisher",
         "faction": "FAC-2",
         "type": "Grunt",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_HO, "stealth counter": C_MH,
         "wall hack": False,
         "health": H_LM, "armour": 0, "damage resistances": F2_RESIT_M,
         "thickness": T_LM, "vel max": V_HO, "speed": 1.5, "friction": 1.5,
         "weapon": "Plasma Rifle",
         "func input": "enemy_input_faction_2_basic",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Skirmisher.png",
         "on death": "none",
         "free var": {}
         },
    # BoomStick	        M	    L/M	    M       M	    M	    M	    M	    M	    Slower, high damage
    "BoomStick":
        {"name": "BoomStick",
         "faction": "FAC-2",
         "type": "Shock",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_MO, "stealth counter": C_MO,
         "wall hack": False,
         "health": H_MO, "armour": A_LM, "damage resistances": F2_RESIT_M,
         "thickness": T_MO, "vel max": V_MO, "speed": 1.5, "friction": 1.5,
         "weapon": "Laser Shotgun",
         "func input": "enemy_input_faction_2_boomstick",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/BoomStick.png",
         "on death": "none",
         "free var": {"Startup lag": 0, "Startup time": 60}
         },
    # Smoker	        M	    L/M	    L       M/H	    M	    M	    M/H	    M	    Throws smoke grenades to conceal other enemies
    "Smoker":
        {"name": "Smoker",
         "faction": "FAC-2",
         "type": "Grunt",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_MO, "stealth counter": C_MH,
         "wall hack": False,
         "health": H_MO, "armour": A_LM, "damage resistances": F2_RESIT_L,
         "thickness": T_MO, "vel max": V_MH, "speed": 1.5, "friction": 1.5,
         "weapon": "Smoke Dispenser",
         "func input": "enemy_input_faction_2_smoker",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Smoker.png",
         "on death": "none",
         "free var": {}
         },
    # Snare	            M	    L/M	    L       L/M	    M	    M	    M	    M	    Debuffs players, no idea how
    "Snare":
        {"name": "Snare",
         "faction": "FAC-2",
         "type": "Grunt",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_LO, "stealth counter": C_MH,
         "wall hack": False,
         "health": H_MH, "armour": A_MO, "damage resistances": F2_RESIT_H,
         "thickness": T_LM, "vel max": V_HO, "speed": 1.5, "friction": 1.5,
         "weapon": "Desert Shotgun",
         "func input": "enemy_input_faction_2_basic",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Snare.png",
         "on death": "none",
         "free var": {}
         },
    # Crusher	        M/H	    M/H	    H       M	    L/M	    M	    M	    M/H	    Destroys armour
    "Crusher":
        {"name": "Crusher",
         "faction": "FAC-2",
         "type": "Grunt",
         "targeting range": R_LM, "targeting angle": 60, "stealth mod": S_MO, "stealth counter": C_MO,
         "wall hack": False,
         "health": H_MH, "armour": A_MH, "damage resistances": F2_RESIT_H,
         "thickness": T_MH, "vel max": V_HO, "speed": 1.5, "friction": 1.5,
         "weapon": "Gun Hammer",
         "func input": "enemy_input_faction_2_crusher",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Crusher.png",
         "on death": "none",
         "free var": {}
         },
    # Assassin	        M/H	    M	    M       H	    M	    H	    M/H	    M	    Tries to flank the player
    "Assassin":
        {"name": "Assassin",
         "faction": "FAC-2",
         "type": "Grunt",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_HO, "stealth counter": C_MH,
         "wall hack": False,
         "health": H_MH, "armour": A_MO, "damage resistances": F2_RESIT_M,
         "thickness": T_MO, "vel max": V_HO, "speed": 1.5, "friction": 1.5,
         "weapon": "Pile Bunker",
         "func input": "enemy_input_faction_2_assassin",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_advanced_gun",
         "sprites": "Sprites/Enemies/Assassin.png",
         "on death": "none",
         "free var": {}
         },
    #                   MHlt	MArm	Resits	Spd 	VisRg	SltMod	SltCntr	Size
    # |Square|----------------------------------------------------------------------------------------------------------
    # Infantry	        M/H	    M/H	    M	    L/M	    M	    L	    M	    M	    Basic and tough.
    "Infantry":
        {"name": "Infantry",
         "faction": "FAC-3",
         "type": "Grunt",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_LO, "stealth counter": C_MO,
         "wall hack": False,
         "health": H_MH, "armour": A_MH, "damage resistances": F3_RESIT_M,
         "thickness": T_MO, "vel max": V_LO, "speed": 1.5, "friction": 1.5,
         "weapon": "Combat Rifle",
         "func input": "enemy_input_faction_3_basic",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Infantry.png",
         "on death": "none",
         "free var": {}
         },
    # Flamer	        M/H	    M/H	    M	    L	    M	    L--	    M	    M/H	    Uses a flamethrower to counter close range attacks.
    "Flamer":
        {"name": "Flamer",
         "faction": "FAC-3",
         "type": "Shock",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_LO, "stealth counter": C_MO,
         "wall hack": False,
         "health": H_MH, "armour": A_MH, "damage resistances": F3_RESIT_M,
         "thickness": T_MO, "vel max": V_LO, "speed": 1.5, "friction": 1.5,
         "weapon": "Flamethrower",
         "func input": "enemy_input_faction_3_basic", "func act": "enemy_act_type_1", "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Flamer.png",
         "on death": "none",
         "free var": {}
         },
    # Spotter	        M/H	    M	    L	    L/M	    M/H	    L/M	    L/M	    M	    Can see through walls. Share targets.
    "Spotter":
        {"name": "Spotter",
         "faction": "FAC-3",
         "type": "Support",
         "targeting range": R_MH, "targeting angle": 60, "stealth mod": S_LO, "stealth counter": C_MO,
         "wall hack": True,
         "health": H_MH, "armour": A_MO, "damage resistances": F3_RESIT_L,
         "thickness": T_MO, "vel max": V_LO, "speed": 1.5, "friction": 1.5,
         "weapon": "Binoculars",
         "func input": "enemy_input_faction_3_spotter", "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Spotter.png",
         "on death": "none",
         "free var": {}
         },
    # Artilleryman      M/H	    M	    M	    L/M	    L/M	    L	    M	    L/M	    Causes artillery strikes
    "Artilleryman":
        {"name": "Artilleryman",
         "faction": "FAC-3",
         "type": "Specialist 1",
         "targeting range": R_LM, "targeting angle": 60, "stealth mod": S_LO, "stealth counter": C_MO,
         "wall hack": False,
         "health": H_MH, "armour": A_MO, "damage resistances": F3_RESIT_M,
         "thickness": T_LM, "vel max": V_LO, "speed": 1.5, "friction": 1.5,
         "weapon": "Artillery Radio",
         "func input": "enemy_input_faction_3_artilleryman", "func act": "enemy_act_type_1", "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Artilleryman.png",
         "on death": "none",
         "free var": {}
         },
    # Grenadier	        M/H	    M/H	    M	    L/M	    M	    L	    L/M	    M/H	    Uses incendiary grenades to deny area
    "Grenadier":
        {"name": "Grenadier",
         "faction": "FAC-3",
         "type": "Specialist 2",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_LO, "stealth counter": C_MO,
         "wall hack": False,
         "health": H_MH, "armour": A_MH, "damage resistances": F3_RESIT_M,
         "thickness": T_MO, "vel max": V_LO, "speed": 1.5, "friction": 1.5,
         "weapon": "Napalm Grenade Launcher",
         "func input": "enemy_input_faction_3_grenade", "func act": "enemy_act_type_1", "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Grenadier.png",
         "on death": "none",
         "free var": {}
         },
    # Bulwark	        H	    H++	    H	    L--	    M	    L--	    M	    H++	    Use minigun. Slow. Scary.
    "Bulwark":
        {"name": "Bulwark",
         "faction": "FAC-3",
         "type": "Elite",
         "targeting range": R_MO, "targeting angle": D_HO, "stealth mod": S_LO, "stealth counter": C_MO,
         "wall hack": False, "health": H_HO, "armour": round(A_HO*1.5), "damage resistances": F3_RESIT_H,
         "thickness": T_HO,
         "vel max": V_LO * 0.8, "speed": V_LO * 0.8, "friction": V_LO * 0.8,
         "weapon": "Bulwark Minigun",

         "func input": "enemy_input_faction_3_bulwark",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_bulwark",
         "sprites": "Sprites/Enemies/Bulwark.png", "on death": "none",
         "free var": {}
         },
    "Commanding Officer":
        {"name": "Commanding Officer",
         "faction": "FAC-3",
         "type": "VIP",
         "targeting range": R_MH, "targeting angle": D_MO, "stealth mod": S_LO, "stealth counter": C_MO,
         "wall hack": False,
         "health": H_HO, "armour": H_LM, "damage resistances": F3_RESIT_L,
         "thickness": T_MO,
         "vel max": V_LM, "speed": 1.5, "friction": 1.5,
         "weapon": "Combat Rifle",

         "func input": "enemy_input_faction_3_basic", "func act": "enemy_act_type_1", "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Commanding Officer.png", "on death": "none",
         "free var": {"Is VIP": True}
         },
    # |Bosses|----------------------------------------------------------------------------------------------------------
    # Armored Shield Generator
    # Hover Tank
    "Hover Tank": {
        "name": "Hover Tank", "faction": "FAC-2",
        "health": H_HO * 20, "armour": 0, "damage resistances": FO_RESIT,
        "sprites": "Sprites/Player/THR-1/Condor.png",

        "thickness": 60, "vel max": V_MO, "speed": 2.2, "friction": 0.7,
        "dash": {"speed": DS_MO * 0.6, "i-frames": 0, "charge": 35},
        # Weapons
        "weapon": "Hover Tank Cannon",
        # AI
        "func input": "hover_tank_input", "func act": "hover_tank_act", "func draw": "hover_tank_draw",
        "on death": "none",
        "targeting range": R_MO, "targeting angle": 180, "stealth mod": S_LO, "stealth counter": C_LM,
        "wall hack": False,
        "free var": {"Move angle": 0,
                     "Machine Gun Angle": -90, "Allow machine gun": False,
                     "IS BOSS": True, "Grenade Shakedown": 600, "Grenade Shakedown angle": 0, "Run people over": 250,
                     "Startup lag": 0, "Startup time": 240}
    },
    # Fire Support Mech
    # Attack Helicopter
    "Attack Helicopter": {
        "name": "Attack Helicopter", "faction": "FAC-3",
        "health": H_HO * 20, "armour": 0, "damage resistances": FO_RESIT,
        "sprites": "Sprites/Player/THR-1/Condor.png",

        "thickness": 60, "vel max": V_MO, "speed": 6.2, "friction": 4,
        "dash": {"speed": DS_MO * 0.6, "i-frames": 0, "charge": 35},
        # Weapons
        "weapon": "Attack Helicopter Weaponry",
        # AI
        "func input": "attack_helicopter_input", "func act": "attack_helicopter_act", "func draw": "attack_helicopter_draw",
        "on death": "none",
        "targeting range": R_MO, "targeting angle": 180, "stealth mod": S_LO, "stealth counter": C_LM,
        "wall hack": False,
        "free var": {"Move angle": 0,
                     "Machine Gun Angle": -90, "Allow machine gun": False,
                     "IS BOSS": True, "Grenade Shakedown": 600, "Grenade Shakedown angle": 0, "Run people over": 250,
                     "Startup lag": 0, "Startup time": 240}
    },

    "VIP":
        {"name": "Nest Trooper",
         "faction": "FAC-1",
         "type": "VIP",
         "targeting range": 450,
         "targeting angle": 25,
         "wall hack": False,
         "health": 200,
         "armour": 100,
         "damage resistances": NO_RESIT_L,
         "thickness": 16,
         "vel max": 3.25,
         "speed": 1.5,
         "friction": 1.5,
         "weapon": "Nest Heavy Machine Gun",

         "func input": "enemy_input_nest_trooper",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Nest Commander.png",
         "on death": "none",
         "free var": {
             "Is VIP": True
         }
         },
}


def how_many_attacks_to_kill_everyone(damage, damage_type):
    for repertory in [player_repertory, enemy_repertory]:
        print("___")
        for count, e in enumerate(repertory):
            health = repertory[e]["health"] + repertory[e]["armour"]
            attack_count = 0
            while health > 0:
                health -= damage * repertory[e]["damage resistances"][damage_type]
                attack_count += 1
            if count % 7 == 0:
                print(count)
            print(f'{repertory[e]["name"]} takes {attack_count} attacks')
# how_many_attacks_to_kill_everyone(250, "Melee")
# "Physical" "Fire" "Explosion" "Energy" "Melee"