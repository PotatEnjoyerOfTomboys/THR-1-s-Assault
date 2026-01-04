import pygame as pg
import sys
import random

import Entity
import Fun
import Bullets
import Items
import Particles


class Upgrade:
    def __init__(self, owner, info):
        self.name = info["name"]
        self.owner = owner
        self.trigger_func = info["trigger"]
        if type(self.trigger_func) == str:
            self.trigger_func = getattr(sys.modules[__name__], self.trigger_func)
        self.effect_func = info["effect"]
        if type(self.effect_func) == str:
            self.effect_func = getattr(sys.modules[__name__], self.effect_func)
        self.activation_count = 0
        self.result = False
        self.free_var = {}

    def act(self, entities, level):
        self.result = self.trigger_func(self, entities, level)
        if self.result:
            self.effect_func(self, entities, level)


# Triggers
def trigger_none(self, entities, level):
    return True


def trigger_when_loaded(self, entities, level):
    # Use this to load upgrades that affect stats
    # Since it should only be used once. Removes the upgrade after it's been used
    for count, u in enumerate(self.owner.upgrades):
        if u == self:
            self.owner.upgrades.pop(count)
            break
    return True


def trigger_standing_still(self, entities, level):
    return self.owner.standing_still


def trigger_max_agro(self, entities, level):
    return self.owner.agro > 90


def trigger_interact_key(self, entities, level):
    return self.owner.input["Interact"] and self.owner.no_shoot_state == 0


def trigger_on_hit(self, entities, level):
    return self.owner.damage_taken and self.owner.status["No damage"] == 7


def trigger_dash(self, entities, level):
    return self.owner.dash_cooldown == self.owner.dash_charge_time - 1


def trigger_on_hit_effect(self, entities, level):
    # This can work as a way to see if someone shot
    return bool(self.owner.bullets_shot)


def trigger_last_stand(self, entities, level):
    return "Last Stand" in self.free_var


def trigger_targeted(self, entities, level):
    return self.owner.is_targeted


def trigger_targeted_return_enemies(self, entities, level):
    result = []
    for e in entities["entities"]:
        if e.target == self.owner:
            result.append(e)
    return result


def trigger_not_targeted(self, entities, level):
    return not self.owner.is_targeted


def trigger_kicking_blue_balls(self, entities, level):
    return self.owner.free_var["Kicked"] >= 10


def trigger_mastermind(self, entities, level):
    # Use this to load upgrades that affect stats
    for x in range(4):
        try:
            e = entities["entities"][x]
            if e.team != self.owner.team:
                break
            if e == self.owner: continue
            if e.skills[1].first_active_frame:
                return True
        except IndexError:
            return False
    return False


def trigger_exposed_blue_balls(self, entities, level):
    if self.owner.is_targeted:
        self.owner.free_var["Exposed blue ball timer"] += 1
    else:
        self.owner.free_var["Exposed blue ball timer"] = 0
    return self.owner.free_var["Exposed blue ball timer"] > 120


def trigger_low_health(self, entities, level):
    for count, u in enumerate(self.owner.upgrades):
        if u == self:
            self.owner.upgrades.pop(count)
            break
    return self.owner.health < self.owner.max_health * 0.33


def trigger_reloading(self, entities, level):
    return self.owner.reloading and self.owner.no_shoot_state == self.owner.weapon.reload_time


def trigger_every_2_sec(self, entities, level):
    return self.owner.time % 120 == 0


def trigger_dragon_breath(self, entities, level):
    if self.owner.status["Burning"] > 0:
        if "Dragon Breath" in self.owner.free_var:
            return False
        self.owner.free_var.update({"Dragon Breath": True})
        return True

    if "Dragon Breath" in self.owner.free_var:
        self.owner.free_var.pop("Dragon Breath")

# Effects
def effect_none(self, entities, level):
    pass


def effect_skill_activate(self, entities, level):
    # Adds the name of the upgrade in the Free var, skill functions check for them to add effects
    self.owner.free_var.update({self.name: True})


def effect_give_blue_balls(self, entities, level):
    # Adds the name of the upgrade in the Free var, skill functions check for them to add effects
    if "Blue Balls" not in self.owner.free_var:
        self.owner.free_var.update({"Blue Balls": []})
    self.owner.free_var["Blue Balls"].append(self.name)


def effect_awareness(self, entities, level):
    self.owner.stealth_counter *= 2
    self.owner.targeting_range *= 1.1


def effect_lucky_shot(self, entities, level):
    # Get weapon name, give crit chance based on that
    self.owner.weapon.crit_rate = {
        # THR-1
        "Saloum Mk-2": 0.13,
        "GMG-04B": 0.075,
        "Big Iron": 0.23,
        # "Big Iron": 0.99,

        "GunBlade": 0.1,
        "Corrine's Old Rifle": 0.11,
        "Oversized stun baton": 0.1,

        "Jeanne's Family Shotgun": 0.12,
        "Custom Mk18 Laser cutter": 0.05,
        "Crippled Laddie FCS Radio": 0.23,

        "St-Maurice": 0.2,
        "St-Laurent Gen 1": 0.15,
        "Mk16 Flare Mortar": 0.1,

        "Chain Axe": 0.25,
        "Hook Swords": 0.25,
        "Gun and Ballistic Knife": 0.25,

        "Epicurean Medic Rifle": 0.24,
        "Nihilist Stretcher": 0.24,
        "Stoic Shield generator": 0.24,

        "Type 41 SMG": 0.11,
        "Type 23 Shotgun": 0.08,
        "Type 47 Rifle": 0.2,

        "Fortress Machine Gun": 0.99,

        # Colonists
        "Standard Shotgun": 0.1, # Shares with Cowboy's Repeater
        "War and Peace": 0.1,
        "Hunk of Steel": 0.1,

        "Lawrence's Cutlass & Flintlock": 0.1,
        "Captain's Axe & Blunderbuss": 0.1,
        "Musket .360": 0.1,

        "Mark's Real Rifle": 0.1,
        "Type 30 Rifle": 0.1,
        "C4": 0.1,

        "Vivianne's Rifle": 0.1,
        "Vivianne's Shotgun": 0.1,
        "Vivianne's Leg": 0.1,

        "Buggy Gun": 0.1
    }[self.owner.weapon.name]


def effect_safe_bet(self, entities, level):
    self.owner.weapon.crit_rate *= 1.5


def effect_all_in(self, entities, level):
    self.owner.weapon.crit_multiplier *= 1.5


def effect_risk_management(self, entities, level):
    self.owner.weapon.crit_rate *= 2


def effect_double_down(self, entities, level):
    self.owner.weapon.crit_multiplier *= 2


def effect_additional_body_armour(self, entities, level):
    self.owner.max_armour = round(self.owner.max_armour * 1.25)
    self.owner.armour = self.owner.max_armour


def effect_reinforced_plates(self, entities, level):
    self.owner.resistances["Physical"] *= 0.75


def effect_fire_retardant_armour(self, entities, level):
    self.owner.resistances["Fire"] *= 0.75


def effect_anti_boom_boom_armour(self, entities, level):
    self.owner.resistances["Explosion"] *= 0.75


def effect_anti_laser_coating(self, entities, level):
    self.owner.resistances["Energy"] *= 0.75


def effect_skill_solution(self, entities, level):
    self.owner.skills[0].recharge_rate *= 1.75
    self.owner.skills[1].recharge_rate *= 1.75
    self.owner.vel_max *= 0.9
    self.owner.targeting_angle *= 0.9


def effect_skill_issue(self, entities, level):
    self.owner.skills[0].recharge_rate *= 0.75
    self.owner.skills[1].recharge_rate *= 0.75
    self.owner.vel_max *= 1.3
    self.owner.targeting_angle *= 1.3


# Lord
def effect_sduddpushbmd(self, entities, level):
    # 		Upgrades Beast Mode. Doubles duration. Lord gets max agro.
    # 		Can't use weapons for 5 sec after the effect ends
    self.owner.free_var.update({self.name: True})
    self.owner.skills[1].depletion_rate /= 2
    # Doubles duration


def effect_3rd_degree(self, entities, level):
    for b in self.owner.bullets_shot:
        b.on_hit.append(Bullets.on_hit_3rd_degree)


def effect_shrapnel(self, entities, level):
    for b in self.owner.bullets_shot:
        b.on_hit.append(Bullets.on_hit_shrapnel)


def effect_rubber_grenades(self, entities, level):
    for b in self.owner.bullets_shot:
        if type(b) != Bullets.Missile:
            b.wall_physics = Bullets.base_grenade_wall_hit
            continue
        b.wall_physics = Bullets.bouncy_missile_wall_hit    # Use dict to give correct option based on weapon


def effect_bigger_booms(self, entities, level):
    # 		Explosions have a bigger growth rate
    bullet_info = self.owner.weapon.bullet_info[4]["Secondary explosion"].copy()
    bullet_info["Growth"] *= 1.75
    self.owner.weapon.bullet_info[4]["Secondary explosion"] = bullet_info


def effect_cant_touch_me(self, entities, level):
    pos = Fun.random_point_in_circle(self.owner.pos, 32)
    entities["particles"].append(
        Particles.RandomParticle1(pos, Fun.DARK_RED, random.random(), round(10 + 10 * random.random()), size=(2, 4))
    )
    self.owner.status["Dash recovery up"] += 1


def effect_remote_detonation(self, entities, level):
    # 		Pressing the interact key lets you detonate your projectiles early, they get a damage boost when doing so
    self.no_shoot_state = 90
    for b in entities["bullets"]:
        if b.owner != self.owner:
            continue
        if type(b) in [Bullets.Missile, Bullets.ExplosionPrimaryType1, Bullets.ExplosionPrimaryType2, Bullets.GrenadeType1]:
            b.duration = -1
            b.damage *= 3
            sec_boom = b.secondary_explosion.copy()
            sec_boom["Growth"] *= 2.5
            entities["bullets"].append(Bullets.ExplosionSecondary(b.pos, b.angle,
                                                                  [0, b.secondary_explosion["Duration"],
                                                                   b.radius,
                                                                   b.damage, b.secondary_explosion], b.owner))
            Particles.random_particle_2_circle(entities, b.pos, 4, 30, 16, colour=Fun.WHITE, size=6, angle_mod=180 * random.random())


def effect_dashing_blue_balls(self, entities, level):
    # Todo: Add sound effect
    for x in range(3):
        Bullets.spawn_blue_balls(
            self.owner, entities,
            Fun.random_point_in_donut(self.owner.pos, [16, 32]),
            self.owner.direction_angle + random.randint(-33, 33),
            [5, 230, 10, 30, {"Colour": Fun.DARK_BLUE}])


# Emperor
def effect_overly_prepared(self, entities, level):
    # Faction, mission_type
    p = [
        {"Capture":             "Double speed",
         "Seek and Destroy":    "Perfect Aim",
         "Eliminate Commander": "Stealth",
         "Defense":             "High res",
         "Escort":              "High res",
         "Defeat Elite Unit":   "Dash recovery up"},

        {"Capture":             "Double speed",
         "Seek and Destroy":    "High res",
         "Eliminate Commander": "Dash recovery up",
         "Defense":             "Perfect Aim",
         "Escort":              "High res",
         "Defeat Elite Unit":   "Perfect Aim"},

        {"Capture":             "Double speed",
         "Seek and Destroy":    "No debuff",
         "Eliminate Commander": "Stealth",
         "Defense":             "No debuff",
         "Escort":              "High res",
         "Defeat Elite Unit":   "Perfect Aim"},
    ][level["faction"]][level["objective"]]

    for e in range(4):
        if entities["entities"][e].team != self.owner.team:
            break
        entities["entities"][e].status[p] += 30 * 60


def effect_skill_skilled(self, entities, level):
    # Adds the name of the upgrade in the Free var, skill functions check for them to add effects
    self.owner.free_var.update({self.name: True})
    for e in entities["entities"]:
        if e.name == self.owner.name:
            continue
        if e.team != self.owner.team:
            continue
        self.owner.free_var.update({e.name: True})


def effect_bad_luck(self, entities, level):
    for e in entities["entities"]:
        if e.team == self.owner.team:
            continue
        if "IS BOSS" in e.free_var:
            continue
        if e.name in [
            "Marksman",
            "Crusher", "Assassin",
            "Bulwark"
        ]:
            continue
        e.upgrades.append(
            Upgrade(e, {
                'Tier': 0, 'Cost': -1000, 'Owner': e.name, 'Icon': None,
                'name': 'Jamming', 'effect': 'effect_bad_luck_jamming', 'trigger': 'trigger_on_hit_effect'},)
        )


def effect_bad_luck_jamming(self, entities, level):
    if random.random() < 0.12:
        self.owner.no_shoot_state = self.owner.weapon.fire_rate * 3
        self.owner.weapon.ammo = 0
        if "Startup lag" in self.owner.free_var:
            self.owner.free_var["Startup lag"] = 0
        for x in range(3):
            pos = Fun.random_point_in_circle(self.owner.pos, 16)
            entities["particles"].append(
                Particles.RandomParticle1(pos, Fun.GRAY, 2, round(10 + 10 * random.random()), size=(2, 4))
            )


def effect_mastermind(self, entities, level):
    # if self.owner.skills[1].recharge >= self.owner.skills[1].recharge_max:
    #     return
    self.owner.skills[1].recharge += self.owner.skills[1].recharge_max * 0.5
    if self.owner.skills[1].recharge > self.owner.skills[1].recharge_max:
        self.owner.skills[1].recharge = self.owner.skills[1].recharge_max

    for x in range(5):
        pos = Fun.random_point_in_circle(self.owner.pos, 16)
        entities["particles"].append(
            Particles.RandomParticle1(pos, Fun.YELLOW, -2, round(10 + 10 * random.random()),
                                size=(1, 4))
        )


def effect_kicking_blue_balls(self, entities, level):
    # Todo: Add sound effect
    for x in range(3):
        Bullets.spawn_blue_balls(
            self.owner, entities,
            Fun.random_point_in_donut(self.owner.pos, [16, 32]),
            self.owner.angle + random.randint(-33, 33),
            [5, 230, 10, 30, {"Colour": Fun.DARK_BLUE}])
    self.owner.free_var["Kicked"] = 0


# Wizard
def effect_engineering_mayhem(self, entities, level):
    # 		Jeanne build skill recharges faster
    self.owner.free_var.update({self.name: True})
    self.owner.skills[0].recharge_rate *= 3


def effect_short_temper(self, entities, level):
    # 		Jeanne get a speed boost and gains time 1.5 resistance for 5 sec after getting hit
    self.owner.status["High res"] = 5 * 60
    self.owner.status["Double speed"] = 5 * 60
    for x in range(10):
        pos = Fun.random_point_in_circle(self.owner.pos, 32)
        entities["particles"].append(
            Particles.RandomParticle1(pos, (64, 64, 128), random.random(), round(10 + 10 * random.random()), size=(2, 4))
        )


def effect_action_girl(self, entities, level):
    # 		Jeanne reloads twice as fast
    self.owner.weapon.reload_time //= 2


# Sovereign
def effect_trick_shot(self, entities, level):
    for b in self.owner.bullets_shot:
        b.wall_physics = Bullets.base_grenade_wall_hit


def effect_scavenge(self, entities, level):
    for b in self.owner.bullets_shot:
        b.on_hit.append(Bullets.on_hit_scavenge)


def effect_duck_and_cover(self, entities, level):
    control = -20
    if self.owner.agro >= control:
        e = self.owner
        for x in range(5):
            pos = Fun.random_point_in_circle(e.pos, 16)
            entities["particles"].append(
                Particles.RandomParticle1(pos, Fun.BLUE, 2, round(10 + 10 * random.random()),
                                    size=(2, 4))
            )
        if self.owner.agro > control + 10:
            self.owner.agro -= 10
        self.owner.agro = control


def effect_stick_more_in(self, entities, level):
    self.owner.weapon.max_ammo *= 2
    self.owner.weapon.ammo = self.owner.weapon.max_ammo


def effect_nothing_to_see(self, entities, level):
    self.owner.agro_decrease_rate = 2


def effect_i_see_you(self, entities, level):
    for b in self.owner.bullets_shot:
        b.on_hit.append(Bullets.on_hit_i_see_you)


def effect_eagle_eye(self, entities, level):
    self.owner.targeting_range *= 1.3
    self.owner.targeting_angle *= 2
    self.owner.stealth_counter *= 2
    self.free_var["Detect Targets Duration"] = 5 * 60


def effect_exposed_blue_balls(self, entities, level):
    self.owner.free_car["Exposed blue ball timer"] = 0
    angle = self.owner.angle
    for x in range(6):
        Bullets.spawn_blue_balls(
            self.owner, entities,
            self.owner.pos.copy(),
            # self.owner.direction_angle + 20 * x ,
            angle + random.uniform(-x, x),
            [3.5, 60, 4 + 3 * random.random(), 20, {"Colour": Fun.DARK_BLUE}])


# Duke
def effect_shadow_walk(self, entities, level):
    self.owner.sound_mod = 0


def effect_out_of_sight_out_of_mind(self, entities, level):
    if self.owner.status["No damage"] < 60:
        self.owner.status["No damage"] = 60
    entities["particles"].append(Particles.Smoke(
            Fun.random_point_in_circle(self.owner.pos, 16),
        ))


# Jester
def effect_out_of_my_way(self, entities, level):
    Items.spawn_item(entities, "M3-D1C OUT OF MY WAY", self.owner.pos.copy(), self=self.owner)
    entities["items"][-1].life_time = abs(self.owner.dash_cooldown)


def effect_improved_hardware(self, entities, level):
    # 		Major Stat increase to; Spd, VisRg, SltMod, DshSpd, DshReco
    self.owner.vel_max = Entity.V_MO
    self.owner.stealth_mod = Entity.S_MH
    self.owner.targeting_range *= Entity.R_MH / Entity.R_LM
    self.owner.dash_speed = Entity.DS_MO
    self.owner.dash_charge_time = 25


def effect_improved_software(self, entities, level):
    # 		Major Stat increase to; VisRg, SltCntr, Driving, Skill recharge rate
    self.owner.targeting_range *= Entity.R_MH / Entity.R_LM
    self.owner.stealth_counter *= 2
    self.owner.driving = Entity.DRIVE_HO
    self.owner.skills[0].recharge_rate *= 2
    self.owner.skills[1].recharge_rate *= 2


def effect_brittle_blue_balls(self, entities, level):
    for x in range(12):
        ran =  random.random()
        Bullets.spawn_blue_balls(
            self.owner, entities,
            self.owner.pos.copy(),
            # self.owner.direction_angle + 20 * x ,
            360 * ran,
            [3.5, 60, 4 + 3 * ran * random.random(), 10, {"Colour": Fun.DARK_BLUE}])


# Condor
def effect_ricochet(self, entities, level):
    for b in self.owner.bullets_shot:
        # b.wall_physics = Bullets.base_grenade_wall_hit
        b.wall_physics = Bullets.condor_ricochet_wall_hit    # Use dict to give correct option based on weapon


def effect_spread(self, entities, level):
    for b in self.owner.bullets_shot:
        # b.wall_physics = Bullets.base_grenade_wall_hit
        b.on_hit.append(Bullets.on_hit_spread)


def effect_intimidation(self, entities, level):
    for b in self.owner.bullets_shot:
        # b.wall_physics = Bullets.base_grenade_wall_hit
        b.on_hit.append(Bullets.on_hit_intimidation)


def effect_fear(self, entities, level):
    for b in self.owner.bullets_shot:
        # b.wall_physics = Bullets.base_grenade_wall_hit
        b.on_hit.append(Bullets.on_hit_fear)


def effect_guardian(self, entities, level):
    self.owner.status["High res"] += 2
    if self.owner.status["High res"] > 60:
        self.owner.status["High res"] = 60
    if self.owner.time % 10 == 0:
        self.owner.agro += 1
        self.owner.agro_decrease_rate = 3 * 60
        Particles.random_particle_2_circle_start_offset(
            entities, self.owner.pos, 64, -2, 20, random.randint(2, 18), colour=Fun.DARK_RED,
            angle_mod=180 * random.random())


def effect_pierce(self, entities, level):
    self.owner.weapon.bullet_info[4].update({"Piercing": True})


def effect_unbreaking_blue_balls(self, entities, level):
    # Todo: Add sound effed
    for x in range(36):
        Bullets.spawn_blue_balls(
            self.owner, entities,
            self.owner.pos.copy(),
            self.owner.direction_angle + 10 * x,
            [3.5, 230, 10, 60, {"Colour": Fun.DARK_BLUE}])
    self.free_var = {}


def effect_menace(self, entities, level):
    for e in entities["entities"]:
        if e.team == self.owner.team:
            continue
        if Fun.distance_between(e.pos, self.owner.pos) < 96:
            e.input["Shoot"] = False
            e.no_shoot_state += 1
            if 'Startup lag' in e.free_var:
                if e.free_var['Startup lag'] > 0:
                    e.free_var['Startup lag'] -= 1


def effect_bullying(self, entities, level):
    for b in self.owner.bullets_shot:
        b.ignore_res = True


def effect_terror(self, entities, level):
    for e in self.result:
        e.status["High friction"] += 2


# Curtis
# -------------------------------------------------------------------------------------------------------------------------------
# Curtis	T1				T2					T3
# 				                     +-	VI, L'Amoureux		---	-+
# 	        III, L'Impératrice	    -+-	VIII, La Justice	---	-+-	XIII, La Mort
# 	        X, La Roue de Fortune	-+-	XI, La Force		---	-+-	XII, Le Pendu
# 	        VII, Le Chariot		    -+-	XIV, Tempérance		---	-+
def effect_chariot(self, entities, level):
    Bullets.spawn_bullet(
        self.owner, entities, Bullets.HomingSword, self.owner.pos.copy(), self.owner.aim_angle,
        [6, 50, 28, 25, {
            "Swing Speed": 0,
            "Swing Limit": [0, 0],
            "Targeting range": 256,
            "Targeting time": 30
        }])


def effect_lovers(self, entities, level):
    for e in entities["entities"]:
        if e.name == self.owner.name:
            continue
        if e.team == self.owner.team:
            return
    info = Entity.player_repertory[self.owner.name].copy()
    info["weapon"] = self.owner.weapon.name
    entities["entities"].append(entities["entities"][1])
    entities["entities"][1] = Entity.Entity(info)

    for sprite_direction in entities["entities"][1].sprites:
        for count, sprite in enumerate(sprite_direction["Walk"]):
            sprite_direction["Walk"][count] = pg.transform.grayscale(sprite)

    entities["entities"][1].pos = Fun.random_point_in_circle(self.owner.pos, 32)
    entities["entities"][1].free_var["Ally waypoint"] = self.owner
    entities["entities"][1].name = "Doppelgänger"


# ?	VIII, La Justice
# 		Strong skill gives a homing effect instead of just redirecting them
def effect_temperance(self, entities, level):
    for b in self.owner.bullets_shot:
        b.on_hit.append(Bullets.on_hit_temperance)


def effect_death(self, entities, level):
    for b in self.owner.bullets_shot:
        b.on_hit.append(Bullets.on_hit_death)


def effect_hanged_man(self, entities, level):
    self.owner.weapon.bullet_info[3] *= 2
    self.free_var.update({"Damage boost": True})


# M	XX, Le Jugement
# 		Blue balls generated by Curtis will explode


# Lawrence -------------------------------------------------------------------------------------------------------------
# Law.	T1				T2					T3
# 	Cremation	---	-|-	Slow Burn	        ---	---	-|
# 				     |-	Spontaneous Combustion  --- -|- Inferno
# 	Salamander	---	---	Dragon's Breath		    ---	-|
# 	Sulfur	---	---	---	Brimstone	        ---	---	---	Hellfire
# 					Burning Blue Balls
def effect_salamander(self, entities, level):
    self.owner.resistances["Fire"] = 0


def effect_dragon_breath(self, entities, level):
    self.owner.status["Burning"] *= 2


# ?	Sulfur
# 		.
# ?	Brimstone
# 		.
# ?	Hellfire
# 		.
def effect_inferno(self, entities, level):
    for x in range (18):
        Bullets.spawn_bullet(
            self.owner, entities, Bullets.Fire, self.owner.pos.copy(), x * 20,
            [3, 90, 9, 15, {"Particle allowed": True, "Burn chance": 1, "Burn duration": 120, "Colour": self.owner.weapon.free_var["Colour"]}])
    self.owner.status["Burning"] = 60


# H	Burning Blue Balls
# 		Hitting an enemy who already have the burning effect generate blue balls
def effect_burning_blue_balls(self, entities, level):
    for b in self.owner.bullets_shot:
        b.on_hit.append(Bullets.on_hit_burning_blue_balls)


# Mark -----------------------------------------------------------------------------------------------------------------
# Mark	T1				T2					T3
# 	Low Pressure Reload	Like a Shadow
# 			    		.	---	---	---	---	.
# 	Slow mark          -|- Disable weapon mark 	---	-|-	Stun Mark
# 	Burning mark       -|-	Helping mark	---	---	-|-
# 					Marked Blue Balls
def effect_low_pressure_reloader(self, entities, level):
    if not self.owner.is_targeted:
        self.owner.no_shoot_state //= 2


def effect_like_a_shadow(self, entities, level):
    self.owner.sound_mod = 0
    self.owner.weapon.volume *= 0.25


# L/M	Slow mark
# 		When reloading, place a mark on a randomly chosen enemy in sight
def effect_slow_mark(self, entities, level):
    potential_victims = []
    target_check = self.owner.targeting_range
    for p in entities["entities"]:
        if p.team == self.owner.team:
            continue
        if Fun.check_point_in_cone(target_check,
                                   self.owner.pos[0], self.owner.pos[1], p.pos[0], p.pos[1],
                                   self.owner.angle, self.owner.targeting_angle * 3) or \
                Fun.check_point_in_cone(target_check,
                                        self.owner.pos[0], self.owner.pos[1], p.pos[0], p.pos[1],
                                        self.owner.angle, self.owner.targeting_angle) \
                or Fun.check_point_in_circle(target_check // 10, self.owner.pos[0], self.owner.pos[1], p.pos[0], p.pos[1]):
            potential_victims.append(p)
    if potential_victims:
        victim = Fun.get_random_element_from_list(potential_victims)
        # Add a mark item
        Items.spawn_item(entities, "Mark", victim.pos, self.owner)
        entities["items"][-1].free_var["Victim"] = victim
        entities["items"][-1].free_var["Colour"] = Fun.BLUISH_GRAY
        entities["items"][-1].thiccness = victim.thiccness * 1.2
        entities["items"][-1].free_var["Payload"] = Items.payload_slow

# M	Burning mark
# 		When hitting enemies 25% chance to place a mark which cause burn on hit
def effect_burning_mark(self, entities, level):
    for b in self.owner.bullets_shot:
        b.on_hit.append(Bullets.on_hit_burning_mark)

# M	Disable weapon mark
# 		When using Smoke Grenade. Multiple random enemies receives a mark which make them lose all ammo in magazine. Bosses are immune. Cancel attacks with startup lag
# M/H	Helping mark
# 		When spotting an enemy with Target Locator. Place a mark that give them a bigger hitbox
# H	Stun mark
# 		When hitting enemies with no bullet remaining in the magazine at the time of hitting. Place a mark that stuns them on hit.
def effect_stun_mark(self, entities, level):
    for b in self.owner.bullets_shot:
        b.on_hit.append(Bullets.on_hit_stun_mark)
# ?	.
# 		.
# ?	.
# 		.
# M	Marked Blue Balls
# 		When a mark is activated, create a blue ball

# Vivianne -------------------------------------------------------------------------------------------------------------
# Viv.	T1				T2					T3
# 	Birna & Sardine		Azura				Makoto
# 	Elecktra	---	---	M (Marisa)
# 	Agatha	---	---	---	Sierra
# 					    Speed Dial
# 					    Conference Call
# 					    Blue Ballin'

def effect_add_summon(self, entities, level):
    # Adds the name of the upgrade in the Free var, skill functions check for them to add effects
    self.owner.free_var["Summon pool"].append(self.name)
# ?	Birna & Sardine
# 		Summons Birna and Sardine. She flies toward enemies and launches Sardine (Sardine is a re-skinned Missile that has piercing and is slow as fuck)
# ?	Elecktra
# 		Summons Elecktra. Doesn't move, she shoots at the target closest to Vivianne
# ?	Agatha
# 		Summons Agatha. Follows, She'll charge at enemies if they get too close.
# ?	M (Marisa)
# 		Summons M. Does a charge toward the biggest group of enemy in range, then an AOE spin attack.
# ?	Azura
# 		Summons Azura. Stays in one place. Lunges at an enemy when they get too close.
# ?	Sierra
# 		Summons Sierra. Follows, shoot enemies with different guns based on range. Stays until out of ammo.
def effect_speed_dial(self, entities, level):
    self.owner.free_var["Summon cooldown time"] //= 2


def effect_conference_call(self, entities, level):
    self.owner.free_var["Summon limit"] = 7
# ?	Makoto
# 		Summons Makoto. Makoto follows Vivianne. She destroys bullets, do combos that stuns enemies
# ?	Blue Ball'in
# 		Summons pass a ball to Vivianne when they disspawn. If Vivianne catches the ball, blue balls are generated