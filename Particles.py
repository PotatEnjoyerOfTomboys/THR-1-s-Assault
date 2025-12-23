from Fun import *

import random
import pygame as pg
import math

# |Particles classes|---------------------------------------------------------------------------------------------------
class ExplosionEffect:
    def __init__(self, pos, duration=15, particles=10, radius=10, particle_growth=5, radius_growth=1):
        # Used to be the explosion effect, removed it cause it was cringe
        self.survive_wipe = False
        self.duration = 0

    def draw(self, WIN, scrolling):
        pass


class NewExplosionEffect:
    def __init__(self, pos, duration=75, particles=7, radius=40, particle_growth=4):
        particles = round(particles)
        self.survive_wipe = True
        # Tweak it to make it look better
        # Position of the particles
        self.pos = pos

        # Other properties
        self.duration = duration
        self.radius = radius
        self.particles = []  # Stores the GrowingCircle particles
        self.smoke_to_add = particles // 3 * 2
        colours_to_use = [DARK, AMBER_LIGHT, DARK_GRAY, AMBER, ORANGE, ORANGE, AMBER_LIGHT]
        alpha = random.randint(185, 250)
        self.biggest_duration = 0
        for x in range(particles):
            duration_to_use = duration // random.uniform(1.25, 4)
            growth_to_use = random.uniform(1, round(particle_growth * 0.75)) / pg.math.clamp(x, 1, 4)
            self.particles.append(GrowingCircleTransparent(random_point_in_circle(self.pos, self.radius),
                                                           colours_to_use[x % len(colours_to_use)],
                                                           growth_to_use,
                                                           duration_to_use,
                                                           random.randint(1, 3),
                                                           0, alpha=alpha))

            if duration_to_use > self.biggest_duration:
                self.biggest_duration = duration_to_use
            alpha -= random.randint(10, 20)

        # Add "shards"
        for x in range(particles * 4):
            duration_to_use = duration // random.uniform(1, 4)
            self.particles.append(Shard(random_point_in_circle(self.pos, self.radius / 3 * 2),
                                        [DARK_GRAY, DARK, GRAY, LIGHT_GRAY, DARK, DARK_GRAY][random.randint(0, 5)],
                                        random.uniform(1, radius / 5),
                                        duration_to_use,
                                        random.randint(-180, 180),
                                        size=random.randint(4, 6),
                                        slow_down=random.uniform(0, 0.75)))
        self.particle_growth = particle_growth

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            if self.duration > self.biggest_duration * 0.9 and random.randint(0, 1) == 1:
                for x in range(self.smoke_to_add):
                    self.particles.append(Smoke(random_point_in_donut(self.pos, [self.radius * 0.75, self.radius * 4]),
                                                [DARK_GRAY, WHITE, WHITE, WHITE, DARK, DARK_GRAY
                                                 ][random.randint(0, 5)]
                                                ))
            for i in self.particles:
                i.draw(WIN, scrolling)

            # Change properties
            self.duration -= 1
            # self.particles += self.particle_growth
            # self.radius += self.radius_growth


class BetelgeuseDeathParticle:
    def __init__(self, pos, duration):
        self.survive_wipe = True
        self.pos = [pos[0], pos[1] - 16]

        # Other properties
        self.duration = duration
        self.particles = []  # Stores the GrowingCircle particles
        # GrowingCircleTransparent
        # Add

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            if self.duration <= 600:
                if self.duration == 600:
                    self.particles.append(SolidColourOverlay(UI_COLOUR_BACKGROUND, 600, 0, fade_in=(60, 3)))
                    play_sound("Betel Death BIGGER")
            else:
                self.particles.append(RandomParticle2(
                    [self.pos[0], self.pos[1]],
                    (int(64 - math.sin(self.duration * 0.025) * 64),
                     int(96 - math.sin(self.duration * 0.035) * 64),
                     int(64 - math.sin(self.duration * 0.005) * 64)),
                    3 * random.random(), 45, 360 * random.random(), size=3))
                if self.duration % 45 == 0:
                    play_sound("Betel Death")
                    mod = random.random()
                    pos = random_point_in_circle(self.pos, 32)
                    self.particles.append(GrowingCircleTransparent(
                        pos, (55, 11, 72), 1 * mod, random.randint(25 + round(20 * mod), 75), 0, 0, alpha=125))

            for i in self.particles:
                i.draw(WIN, scrolling)

            self.duration -= 1


class BeastModeParticle:
    def __init__(self, pos, duration, colour):
        self.survive_wipe = True
        self.pos = pos

        # Other properties
        self.duration = duration
        self.colour = colour
        self.particles = []  # Stores the GrowingCircle particles
        # GrowingCircleTransparent
        # Add

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            # p, [angle, dist, size, speed]
            speed = 1 + 3 * random.random()
            info = [360 * random.random(), random.randint(45, 90) * speed, get_random_element_from_list([1, 1, 2]), speed]
            self.particles.append(info)

            for count, i in enumerate(self.particles):
                pos = move_with_vel_angle(self.pos, i[1], i[0])
                half_thick = i[2]//2
                pg.draw.rect(WIN, self.colour, [pos[0] + scrolling[0] - half_thick,
                                                pos[1] + scrolling[1] - half_thick, i[2], i[2]])
                i[1] -= i[3]
                if i[1] < 0:
                    self.particles.pop(count)


            self.duration -= 1


class FireParticle:
    def __init__(self, pos, colour=(220, 0, 0)):
        # Update that
        self.survive_wipe = False
        self.pos = pos
        self.duration = random.randint(5, 12)
        self.colour = colour

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            pg.draw.rect(WIN, self.colour, [self.pos[0] + random.randint(-2, 2) + scrolling[0],
                                            self.pos[1] + random.randint(-2, 2) + scrolling[1],
                                            2, 2])
            self.pos[0] += random.randint(-1, 1)
            self.pos[1] -= random.randint(1, 3)
            self.duration -= 1


class Shard:
    def __init__(self, pos, colour, speed, duration, angle, size=4, slow_down=0):
        self.survive_wipe = False
        # Unused
        self.pos = pos
        self.colour = colour
        self.speed = speed
        self.slow_down = slow_down
        self.duration = duration
        self.angle = angle
        self.points = []

        minimum = [0, 0]
        for x in [[1, 1], [-1, 1], [1, -1], [-1, -1]]:
            sizes = [pg.math.clamp(random.randint(size // 4, size), minimum[0], size),
                     pg.math.clamp(random.randint(size // 4, size), minimum[1], size)]
            for y in range(2):
                if sizes[y] <= size // 2:
                    minimum[y] = size // 3 * 2
                else:
                    minimum[y] = 0

            new_point = (sizes[0] * x[0], sizes[1] * x[1])
            self.points.append(new_point)

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            # This is terrible, too bad
            pg.draw.polygon(WIN, self.colour, [
                [self.pos[0] + self.points[0][0] + scrolling[0], self.pos[1] + self.points[0][1] + scrolling[1]],
                [self.pos[0] + self.points[1][0] + scrolling[0], self.pos[1] + self.points[1][1] + scrolling[1]],
                [self.pos[0] + self.points[2][0] + scrolling[0], self.pos[1] + self.points[2][1] + scrolling[1]],
                [self.pos[0] + self.points[3][0] + scrolling[0], self.pos[1] + self.points[3][1] + scrolling[1]]
            ])
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)
            # self.pos = move_with_vel_angle(self.pos, self.speed, self.angle)
            self.duration -= 1
            if self.speed > 0:
                self.speed -= self.slow_down
            else:
                self.speed = 0


class Chain:    # That for Zan'dr's axe
    def __init__(self, pos, colour, duration, angle):
        self.survive_wipe = False
        # Unused
        self.pos = pos
        self.colour = colour
        self.duration = duration
        self.angle = angle

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            for x in [1, -1]:
                start = [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]]
                end_1 = move_with_vel_angle([start[0], start[1]], 5, self.angle + 45 * x)
                end_2 = move_with_vel_angle([end_1[0], end_1[1]], 20, self.angle)
                end_3 = move_with_vel_angle([end_2[0], end_2[1]], 5, self.angle - 45 * x)
                pg.draw.line(WIN, self.colour, start, end_1, 3)
                pg.draw.line(WIN, self.colour, end_1, end_2, 3)
                pg.draw.line(WIN, self.colour, end_2, end_3, 3)

            self.duration -= 1


class LineParticle:
    def __init__(self, pos, colour, duration, length, angle, width=4, vel=0):
        self.survive_wipe = False
        # Unused
        self.pos = pos
        self.colour = colour
        self.duration = duration
        self.angle = angle
        self.length = length
        self.width = width
        self.vel = vel
        self.end_point = move_with_vel_angle(self.pos, self.length, self.angle)

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            pg.draw.line(WIN, self.colour,
                         [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                         [self.end_point[0] + scrolling[0], self.end_point[1] + scrolling[1]], self.width)
            self.pos = move_with_vel_angle(self.pos, self.vel, self.angle)
            self.end_point = move_with_vel_angle(self.pos, self.length, self.angle)
            self.duration -= 1


class LineParticleAlt:
    def __init__(self, point_1: list, point_2: list, colour, duration, width=4):
        self.survive_wipe = False
        self.pos = point_1
        self.colour = colour
        self.duration = duration
        self.width = width
        self.end_point = point_2

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            pg.draw.line(
                WIN, self.colour,
                [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                [self.end_point[0] + scrolling[0], self.end_point[1] + scrolling[1]],
                self.width
            )
            self.duration -= 1


class RealityRift:
    def __init__(self, pos, duration=8000):
        self.survive_wipe = True
        # Unused
        self.pos = pos
        self.colour = (random.randint(0, 255),
                       random.randint(0, 255),
                       random.randint(0, 255))
        self.duration = duration
        # Branch
        angle = 360 * random.random()
        self.branches = [
            {"Start pos": self.pos, "Angle": angle, "Growth rate": 0.25 + 1 * random.random(),
             "Growth time": random.randint(90, 180), "Width": random.randint(4, 5), "Dist": 0},
            {"Start pos": self.pos, "Angle": angle + random.randint(60, 300), "Growth rate": 0.25 + 1 * random.random(),
             "Growth time": random.randint(90, 180), "Width": random.randint(4, 5), "Dist": 0},
            {"Start pos": self.pos, "Angle": angle + random.randint(60, 300),
             "Growth rate": 0.25 + 1 * random.random(),
             "Growth time": 30 * random.randint(4, 10), "Width": random.randint(4, 5), "Dist": 0}
        ]
        self.stage = 1

    def expend(self, WIN, scrolling):
        # Expend stage

        for b in self.branches:
            if b["Growth time"] > 0:
                b["Growth time"] -= 1
                b["Dist"] += b["Growth rate"]
                if b["Growth time"] == 0 and b["Width"] > 1:
                    # Create new branches
                    for p in range(random.randint(1, 3)):
                        self.branches.append(
                                {"Start pos": move_with_vel_angle(b["Start pos"], b["Dist"], b["Angle"]),
                                 "Angle": b["Angle"] + random.uniform(-135, 135),
                                 "Growth rate": 0.25 + 1 * random.random(),
                                 "Growth time": 15 * random.randint(3, 7),
                                 "Width": b['Width'] - 1,
                                 "Dist": 0}
                            )

            pos_1 = b["Start pos"]
            pos_2 = move_with_vel_angle(pos_1, b["Dist"], b["Angle"])

            pg.draw.line(WIN, self.colour,
                             [pos_1[0] + scrolling[0], pos_1[1] + scrolling[1]],
                             [pos_2[0] + scrolling[0], pos_2[1] + scrolling[1]],
                             b["Width"])

        # Handle colour
        self.colour = (int(64 - math.sin(self.duration * 0.025) * 64),
                           int(96 - math.sin(self.duration * 0.035) * 64),
                           int(64 - math.sin(self.duration * 0.005) * 64))
        self.duration -= 1
        if self.duration == 0:
            self.duration = BIG_INT
            self.stage = 0

    def fissle(self, WIN, scrolling):
        if self.duration > 0:
            # Go through all branches
            branch_lists = [
                0, # Always empty
                0, # 1
                0, # 2
                0, # 3
                0, # 4
                0, # 5
            ]
            for b in self.branches:
                # Put them in separate lists based on width
                branch_lists[b["Width"]] += 1

            # Make the one with the smallest width retrack
            width_to_retract = 6
            for count, n in enumerate(branch_lists):
                if count == 0:
                    continue
                if n == 0:
                    continue
                width_to_retract = count
                break
            # Draw the shit
            for b in self.branches:
                if b["Width"] == width_to_retract:
                    b["Dist"] -= b["Growth rate"] * 2
                    if b["Dist"] <= 0:
                        b["Width"] = 0
                        b["Growth rate"] = 0
                        b["Dist"] = 0

                pos_1 = b["Start pos"]
                pos_2 = move_with_vel_angle(pos_1, b["Dist"], b["Angle"])

                pg.draw.line(WIN, self.colour,
                             [pos_1[0] + scrolling[0], pos_1[1] + scrolling[1]],
                             [pos_2[0] + scrolling[0], pos_2[1] + scrolling[1]],
                             b["Width"])

            # Handle colour
            self.colour = (int(64 - math.sin(self.duration * 0.025) * 64),
                           int(96 - math.sin(self.duration * 0.035) * 64),
                           int(64 - math.sin(self.duration * 0.005) * 64))
            self.duration -= 1
            if width_to_retract == 6:
                self.duration = 0

    def draw(self, WIN, scrolling):
        [self.fissle, self.expend][self.stage](WIN, scrolling)


class AimPoint:
    __slots__=['survive_wipe', 'pos', 'colour', 'duration'] # Start to put slots to help with memory
    def __init__(self, pos):
        self.survive_wipe = True
        # Unused
        self.pos = pos
        self.colour = BLUE
        self.duration = 1

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            pg.draw.line(WIN, self.colour,
                         [self.pos[0] + scrolling[0] - 3, self.pos[1] + scrolling[1]],
                         [self.pos[0] + scrolling[0] + 4, self.pos[1] + scrolling[1]], 2)
            pg.draw.line(WIN, self.colour,
                         [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1] - 4],
                         [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]], 2)
            self.duration = 0


class RandomParticle1:
    def __init__(self, pos, colour, speed, duration, size=(2, 4)):
        self.survive_wipe = False
        # Unused
        self.pos = pos
        self.colour = colour
        self.speed = speed
        self.duration = duration
        self.size = size

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            pg.draw.rect(WIN, self.colour, [self.pos[0] + scrolling[0],
                                            self.pos[1] + scrolling[1], self.size[0], self.size[1]])
            self.pos[1] += self.speed
            self.duration -= 1


class RandomParticle2:
    def __init__(self, pos, colour, speed, duration, angle, size=4):
        self.survive_wipe = False
        # Unused
        self.pos = pos
        self.colour = colour
        self.speed = speed
        self.duration = duration
        self.angle = angle
        self.size = size

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            pg.draw.rect(WIN, self.colour, [self.pos[0] + scrolling[0],
                                            self.pos[1] + scrolling[1], self.size, self.size])
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)
            # self.pos = move_with_vel_angle(self.pos, self.speed, self.angle)
            self.duration -= 1


class RandomParticle3:
    def __init__(self, pos, colour, speed, duration, angle, angle_deviation, size=4):
        self.survive_wipe = False
        # Unused
        self.pos = pos
        self.colour = colour
        self.speed = speed
        self.duration = duration
        self.angle = angle
        self.angle_deviation = angle_deviation
        self.size = size

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            pg.draw.rect(WIN, self.colour, [self.pos[0] - self.size // 2 + scrolling[0],
                                            self.pos[1] - self.size // 2 + scrolling[1], self.size, self.size])
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)
            # self.pos = move_with_vel_angle(self.pos, self.speed, self.angle)
            self.duration -= 1
            self.angle += self.angle_deviation


class RandomParticle4:
    def __init__(self, pos, colour, speed, vertical_speed, duration, angle, angle_deviation, size=4):
        self.survive_wipe = False
        # Unused
        self.pos = pos
        self.colour = colour
        self.speed = speed
        self.vertical_speed = vertical_speed
        self.duration = duration
        self.angle = angle
        self.angle_deviation = angle_deviation
        self.size = size

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            pg.draw.rect(WIN, self.colour, [self.pos[0] - self.size // 2 + scrolling[0],
                                            self.pos[1] - self.size // 2 + scrolling[1], self.size, self.size])
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)
            # self.pos = move_with_vel_angle(self.pos, self.speed, self.angle)

            self.pos[1] -= self.vertical_speed
            self.duration -= 1
            self.angle += self.angle_deviation


class MissileLockOn:
    def __init__(self, pos, duration, locked=True, colour=GREEN):
        self.survive_wipe = False

        self.pos = pos
        self.duration = duration
        self.locked=locked
        self.colour =  colour

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            center = self.pos
            pg.draw.rect(WIN, self.colour, [center[0] - 14 + scrolling[0],
                                      center[1] - 14 + scrolling[1],
                                      28,
                                      28], 2)
            if self.locked:
                pg.draw.lines(WIN, self.colour, True, (
                    [center[0] - 14 + scrolling[0], center[1] + scrolling[1]],
                    [center[0] + scrolling[0], center[1] - 14 + scrolling[1]],
                    [center[0] + 14 + scrolling[0], center[1] + scrolling[1]],
                    [center[0] + scrolling[0], center[1] + 14 + scrolling[1]],
                ), 1)
            self.duration -= 1


class CrippleLaddieUI:
    def __init__(self, jeanne):
        self.survive_wipe = True

        self.pos = jeanne.mouse_pos
        self.jeanne = jeanne
        self.duration = 1
        self.colour = GREEN
        self.size = 128

        temp_font = create_temp_font_1(450)
        self.instruct_1 = temp_font.render(f"{write_control(jeanne, "Interact")}: Switch", True, self.colour)
        self.instruct_2 = temp_font.render(f"{write_control(jeanne, "Alt fire")}: Fire", True, self.colour)

        self.text = temp_font.render(
            [
                "HE", "SMK", "FLR"
            ][jeanne.weapon.free_var["Ammo"]], True, self.colour)
        self.text_pos = [
            self.pos[0] - self.size / 2 + 6,
            self.pos[1] - self.size / 2 + 6,
        ]

    def draw(self, WIN, scrolling):
        if self.duration > 0:

            # Fade in
            WIN.blit(self.instruct_1, [self.text_pos[0] + scrolling[0], self.text_pos[1] + scrolling[1] - 6])
            WIN.blit(self.instruct_2, [self.text_pos[0] + scrolling[0], self.text_pos[1] + scrolling[1] + 8])
            WIN.blit(self.text, [self.text_pos[0] + scrolling[0], self.text_pos[1] + scrolling[1] + self.size - 20])
            center = self.pos
            mod = self.size/2
            pain = lambda a : 8 * (a * -1)
            for x in [
                [1, 1],
                [1, -1],
                [-1, 1],
                [-1, -1],
            ]:
                pg.draw.lines(WIN, self.colour, True, (
                    [center[0] + mod * x[0] + scrolling[0] + pain(x[0]), center[1] + mod * x[1] + scrolling[1]],
                    [center[0] + mod * x[0] + scrolling[0], center[1] + mod * x[1] + scrolling[1]],
                    [center[0] + mod * x[0] + scrolling[0], center[1] + mod * x[1] + scrolling[1]+ pain(x[1])],
                ), 2)

            # pg.draw.rect(WIN, self.colour, [center[0] - self.size/2 + scrolling[0],
            #                           center[1] - self.size/2 + scrolling[1],
            #                           self.size, self.size], 2)
            # self.weapon.free_var["Ammo"]
            self.duration -= 1


class GrowingSquare:
    def __init__(self, square, colour, growth, duration, centered=False, thiccness=0):
        self.survive_wipe = False

        pos = [square[0], square[1]]
        width = square[2]
        height = square[3]

        self.pos = pos
        self.colour = colour
        self.growth = growth
        self.duration = duration
        self.width = width
        self.height = height
        self.thiccness = thiccness

        self.centered = centered
        self.offset = [0, 0]
        if self.centered:
            self.offset = [self.width // 2, self.height // 2]

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            pg.draw.rect(WIN, self.colour, [self.pos[0] + scrolling[0] + self.offset[0],
                                            self.pos[1] + scrolling[1] + self.offset[1],
                                            self.width,
                                            self.height], self.thiccness)
            self.width += self.growth[0]
            self.height += self.growth[1]
            self.duration -= 1

            if self.centered:
                self.offset = [self.width // 2, self.height // 2]


class TransparentPolygon:
    def __init__(self, points, colour, duration, alpha):
        self.survive_wipe = False
        self.points = points
        # self.pos = pos
        self.colour = colour
        self.duration = duration
        self.alpha = alpha

        # self.centered = centered
        # self.offset = [0, 0]
        # if self.centered:
        #     self.offset = [self.width // 2, self.height // 2]

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            # pp = [[int(p[0] + scrolling[0]), int(p[1] + scrolling[1])] for p in self.points]
            draw_transparent_poly(
                WIN,
                # pp,
                self.points,
                self.colour, self.alpha, scrolling, width=0)
            # .draw.polygon(WIN, self.colour, pp)
            self.duration -= 1


class GrowingSquareTransparent:
    def __init__(self, square, colour, growth, duration, alpha, centered=False):
        self.survive_wipe = False

        pos = [square[0], square[1]]
        width = square[2]
        height = square[3]

        self.pos = pos
        self.colour = colour
        self.growth = growth
        self.duration = duration
        self.width = width
        self.height = height
        self.alpha = alpha

        self.centered = centered
        self.offset = [0, 0]
        if self.centered:
            self.offset = [self.width // 2, self.height // 2]

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            draw_transparent_rect(WIN, [self.pos[0] + scrolling[0] + self.offset[0],
                                        self.pos[1] + scrolling[1] + self.offset[1],
                                        self.width,
                                        self.height],
                                  self.colour,
                                  self.alpha)

            self.width += self.growth[0]
            self.height += self.growth[1]
            self.duration -= 1

            if self.centered:
                self.offset = [self.width // 2, self.height // 2]


class SolidColourOverlay:
    def __init__(self, colour, duration, alpha, fade_in=(), fadeout=()):
        self.survive_wipe = False

        self.colour = colour
        self.duration = duration
        self.alpha = alpha

        self.fade_in = fade_in
        self.fadeout = fadeout

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            # Handles fade in and out
            if self.fade_in:
                if self.fade_in[0] < self.duration:
                    self.alpha += self.fade_in[1]
            if self.fadeout:
                if self.fadeout[0] > self.duration:
                    self.alpha -= self.fadeout[1]
                    # Ends the particle early if it fades out fast enough
                    if self.alpha <= 0:
                        self.duration = 0
            draw_transparent_rect(WIN, [0, 0, WIN.get_width(), WIN.get_height()], self.colour, self.alpha)
            self.duration -= 1


class NightVisionOverlay:
    def __init__(self, duration):
        self.survive_wipe = False
        self.duration = duration

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            WIN.blit(pg.transform.grayscale(WIN), (0, 0))
            draw_transparent_rect(WIN, [0, 0, WIN.get_width(), WIN.get_height()], (0, 255, 0), 64)

            self.duration -= 1


class GrowingCircle:
    def __init__(self, pos, colour, growth, duration, radius, width):
        self.survive_wipe = False

        self.pos = pos
        self.colour = colour
        self.growth = growth
        self.duration = duration
        self.radius = radius
        self.width = width

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            pg.draw.circle(WIN, self.colour, [self.pos[0] + scrolling[0],
                                              self.pos[1] + scrolling[1]], self.radius, self.width)
            self.radius += self.growth
            self.duration -= 1


class GrowingCircleTransparent:
    def __init__(self, pos, colour, growth, duration, radius, width, alpha=125):
        self.survive_wipe = False

        self.pos = pos
        self.colour = colour
        self.alpha = alpha
        self.growth = growth
        self.duration = duration
        self.radius = radius
        self.width = width

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            draw_transparent_circle(WIN, [self.pos[0] - self.radius + scrolling[0],
                                          self.pos[1] - self.radius + scrolling[1],
                                          self.radius * 2],
                                    self.colour, self.alpha)
            self.radius += self.growth
            self.duration -= 1


class GrowingCircleEntityBound:
    def __init__(self, owner, colour, status, width):
        self.survive_wipe = False
        self.owner = owner
        self.pos = owner.pos
        self.colour = colour
        self.duration = 1
        self.radius = owner.thiccness
        self.status = status
        self.width = width

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            if self.owner.health <=0:
                self.duration = 0
                return
            pg.draw.circle(WIN, self.colour, [self.pos[0] + scrolling[0],
                                              self.pos[1] + scrolling[1]], self.radius, self.width)

            self.duration = self.owner.status[self.status]


class SnowParticle:
    def __init__(self, pos):
        # That's an old one
        self.survive_wipe = False
        self.pos = pos
        self.duration = random.randint(150, 250)

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            pg.draw.rect(WIN, (220, 220, 220), [self.pos[0] + random.randint(-2, 2) + scrolling[0],
                                                self.pos[1] + random.randint(-2, 2) + scrolling[1],
                                                4, 4])
            self.pos[0] -= random.uniform(0.1, 1)
            self.pos[1] += random.randint(2, 5)
            self.duration -= 1


class Smoke:
    def __init__(self, pos, colour=WHITE, duration=(50, 150)):
        self.survive_wipe = False
        self.thiccness = random.randint(2, 8)
        self.pos = random_point_in_circle(pos, 3)
        self.pos = [self.pos[0] - self.thiccness // 2,
                    self.pos[1] - self.thiccness // 2]
        self.duration = random.randint(duration[0], duration[1])
        self.alpha = 255
        self.colour = colour

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            s = pg.Surface((self.thiccness, self.thiccness))  # the size of your rect
            s.set_alpha(self.alpha)  # alpha level
            s.fill(self.colour)  # this fills the entire surface
            WIN.blit(s, (self.pos[0] - self.thiccness // 2 + scrolling[0],
                         self.pos[1] - self.thiccness // 2 + scrolling[1]))
            self.alpha -= 1
            self.duration -= 1


class Flashbang:
    def __init__(self, colour=WHITE, duration=350):
        self.survive_wipe = True
        self.duration = duration
        self.alpha = 255
        self.colour = colour

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            win_width, win_height = WIN.get_size()
            draw_transparent_rect(WIN, (0, 0, win_width, win_height), self.colour, self.alpha)
            if self.duration < 255:
                self.alpha = self.duration
            self.duration -= 1


class Glitch:
    def __init__(self, pos):
        # Not used for anything and not working as intended
        self.survive_wipe = False
        self.thiccness = [random.randint(2, 64), random.randint(2, 64)]
        self.pos = random_point_in_circle(pos, 10)
        self.pos = [self.pos[0] - self.thiccness[0] // 2,
                    self.pos[1] - self.thiccness[1] // 2]
        self.duration = random.randint(25, 60)
        self.colour = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.alpha = 255

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            s = pg.Surface((self.thiccness[0], self.thiccness[1]))  # the size of your rect
            s.set_alpha(self.alpha)  # alpha level
            s.fill(self.colour)  # this fills the entire surface
            WIN.blit(s, (self.pos[0] - self.thiccness[0] // 2 + scrolling[0],
                         self.pos[1] - self.thiccness[1] // 2 + scrolling[1]))
            self.alpha -= 1
            self.duration -= 1


class FishingLine:
    def __init__(self, start_pos, end_pos, colour, duration):
        self.survive_wipe = False
        # Unused
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.colour = colour
        self.duration = duration

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            # pg.draw.arc(WIN, self.colour, [210, 75, 150, 125], start_angle, stop_angle, width=1)
            pg.draw.aaline(WIN, self.colour,
                           [self.start_pos[0] + scrolling[0], self.start_pos[1] + scrolling[1]],
                           [self.end_pos[0] + scrolling[0], self.end_pos[1] + scrolling[1]], True)
            self.duration -= 1


class RainParticle:
    def __init__(self, pos, colour=WATER_NORMAL):
        self.survive_wipe = False
        # Unused
        self.pos = pos
        self.duration = random.randint(125, 250)
        self.mode = 0
        self.particles = []
        self.colour = colour

    def falling(self, WIN, scrolling):
        if self.duration > 0:
            pg.draw.rect(WIN, self.colour, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1], 2, 4])
            self.pos[0] -= random.uniform(0.1, 1)
            self.pos[1] += random.randint(2, 5)
            self.duration -= 1
        if self.duration == 0:
            self.duration += 50
            self.mode = 1
            for x in range(3):
                deez_nuts = random.randint(0, 1)
                angle = [0, 180][deez_nuts] + random.randint(-5, 5)
                angle_deviation = [-4, 4][deez_nuts] + random.randint(-2, 2)
                self.particles.append(
                    RandomParticle3([self.pos[0], self.pos[1]], self.colour, random.uniform(0.5, 2.5),
                                    random.randint(10, 20), angle, angle_deviation, size=random.randint(1, 3)))

    def touch_ground(self, WIN, scrolling):
        if self.duration > 0:
            for i in self.particles:
                i.draw(WIN, scrolling)
            self.duration -= 1

    def draw(self, WIN, scrolling):
        [self.falling, self.touch_ground][self.mode](WIN, scrolling)


class FloatingText:
    def __init__(self, pos, size, text, color, alpha_growth=1, alpha_ungrowth=15):
        self.survive_wipe = True  # Should it survive FPS boosting measures
        self.duration = 2
        self.text = pg.font.SysFont("system", size).render(text, True, color)
        self.pos = [pos[0] - self.text.get_width() // 2,
                    pos[1] - self.text.get_height() // 2]
        self.alpha = 0
        self.alpha_growth = alpha_growth
        self.alpha_ungrowth = alpha_ungrowth

    def draw(self, WIN, scrolling):
        # Fade in
        if self.duration == 2:
            self.text.set_alpha(self.alpha)
            WIN.blit(self.text, [self.pos[0] + scrolling[0],
                                 self.pos[1] + scrolling[1]])

            self.alpha += self.alpha_growth
            if self.alpha >= 255:
                self.text.set_alpha(self.alpha)
                WIN.blit(self.text, [self.pos[0] + scrolling[0],
                                     self.pos[1] + scrolling[1]])
                self.duration = 1
        # Fade out
        elif self.duration == 1 and self.alpha > 0:
            self.text.set_alpha(self.alpha)
            WIN.blit(self.text, [self.pos[0] + scrolling[0],
                                 self.pos[1] + scrolling[1]])

            self.alpha -= self.alpha_ungrowth
        elif self.duration == 1 and self.alpha <= 0:
            self.duration = 0


class FloatingTextType2:
    def __init__(self, pos, size, text, color, duration):
        # This version doesn't fate out
        self.survive_wipe = True  # Should it survive FPS boosting measures
        self.duration = duration
        self.text = pg.font.SysFont("system", size).render(text, True, color)
        self.pos = [pos[0] - self.text.get_width() // 2,
                    pos[1] - self.text.get_height() // 2]

    def draw(self, WIN, scrolling):
        # Fade in
        if self.duration > 0:
            WIN.blit(self.text, [self.pos[0] + scrolling[0],
                                 self.pos[1] + scrolling[1]])

            self.duration -= 1


class FloatingTextType3:
    def __init__(self, pos, size, text, color, duration):
        # This version doesn't fate out
        self.survive_wipe = True  # Should it survive FPS boosting measures
        self.duration = duration
        self.text = pg.font.SysFont("system", size).render(text, True, color)
        self.pos = pos

    def draw(self, WIN, scrolling):
        # Fade in
        if self.duration > 0:
            WIN.blit(self.text, [self.pos[0] + scrolling[0],
                                 self.pos[1] + scrolling[1]])

            self.duration -= 1


class MissionStartText:
    def __init__(self, pos, text, duration, size=50, color=WHITE):
        self.survive_wipe = True  # Should it survive FPS boosting measures
        self.duration = duration
        self.text = pg.font.SysFont("system", size).render(text, True, color)
        self.pos = [pos[0] - self.text.get_width() // 2,
                    pos[1] - self.text.get_height() // 2]

    def draw(self, WIN, scrolling):
        # Fade in
        if self.duration > 0:
            WIN.blit(self.text, self.pos)
            self.duration -= 1
        #


class RadioTransmission:
    def __init__(self, sprite, text, colour, duration, extra_parts=()):
        self.survive_wipe = True  # Should it survive FPS boosting measures
        self.duration = duration
        self.sprite = sprite
        self.text = text
        self.translate_text()
        self.colour = colour
        # self.text = []
        # for x in text:
        #     self.text.append(pg.font.SysFont("system", 25).render(x, True, color))
        # self.pos = [pos[0] - self.text.get_width() // 2,
        #             pos[1] - self.text.get_height() // 2]
        self.extra_parts = extra_parts

    def draw(self, WIN, scrolling):
        # Fade in
        if self.duration > 0:
            zoom = FRAME_MAX_SIZE[0] / 630
            # Draws the text box
            width = WIN.get_width()
            height = WIN.get_height()

            high_point = height - 24 - 64 * zoom
            left_point = width // 2 - 303 * zoom
            draw_transparent_rect(WIN, [left_point, high_point - 4, round(606 * zoom), round(72 * zoom)],
                                  (25, 25, 25), 125)

            # Draws the sprite
            WIN.blit(pg.transform.scale_by(self.sprite, zoom), [left_point + 6, high_point])

            # Writes the text
            y_mod = 0
            # Recheck text because that line might have broken everything
            temp_font = pg.font.SysFont("system", round(0.06 * height))
            for text_to_draw in self.text:
                text_sprite = temp_font.render(text_to_draw, True, self.colour)
                WIN.blit(text_sprite, [left_point + 6 + (68 * zoom), high_point + y_mod])
                y_mod += text_sprite.get_height()

            self.duration -= 1
        if self.duration == 0 and self.extra_parts:
            # Handle the extra "slices" of transmissions
            self.sprite = self.extra_parts[0][0]

            self.text = self.extra_parts[0][1]
            self.translate_text()
            self.colour = self.extra_parts[0][2]
            self.duration = self.extra_parts[0][3]
            self.extra_parts.pop(0)

    def translate_text(self):
        if type(self.text) == str:
            self.text = write_textline(self.text, send_back=True)
            # description = Fun.split_text(description, limit=50)
            no_seperator = self.text.split("||")
            new_description = []
            for section in no_seperator:
                for x in split_text(section, limit=55):
                    new_description.append(x)
            self.text = new_description
        #
    #


class MissionTitleCard:
    def __init__(self, top_text, bottom_text, duration=180, size=50, color=WHITE):
        self.survive_wipe = True  # Should it survive FPS boosting measures
        self.start_duration = duration
        self.duration = duration

        self.top_text = pg.font.SysFont("system", size).render(top_text, True, color)
        self.top_text_width = self.top_text.get_width() // 2
        self.top_text_height = self.top_text.get_height() // 2

        self.bottom_text = pg.font.SysFont("system", size).render(bottom_text, True, color)
        self.bottom_text_width = self.bottom_text.get_width() // 2
        self.bottom_text_height = self.bottom_text.get_height() // 2

        self.text_alpha = 255

        self.rects = [pg.Rect(0, 0, 0, 0),
                      pg.Rect(0, 0, 0, 0)]
        # shrink_rate = self.start_duration // 2

    def draw(self, WIN, scrolling):
        # Fade in
        if self.duration > 0:
            width, height = WIN.get_size()

            # Change height of the rects
            if self.duration == self.start_duration:
                rect_height = height // 5
            else:
                rect_height = self.rects[0].height
            if self.duration <= self.start_duration // 3 * 2 and self.rects[0].height > 1:
                rect_height -= (height // 5) // (self.duration // 3 * 2)
                if rect_height < 0:
                    rect_height = 0
            self.rects[0] = pg.Rect(0, 0, width, rect_height)
            self.rects[1] = pg.Rect(0, height - rect_height, width, rect_height)

            # Draw the rects
            draw_transparent_rect(WIN, self.rects[0], BLACK, 175)
            draw_transparent_rect(WIN, self.rects[1], BLACK, 175)

            # Draw Text
            if self.duration <= self.start_duration // 3 * 2:
                self.text_alpha -= 4
                self.top_text.set_alpha(self.text_alpha)
                self.bottom_text.set_alpha(self.text_alpha)
            WIN.blit(self.top_text,
                     [width // 2 - self.top_text_width, height // 5 - self.top_text_height])
            WIN.blit(self.bottom_text,
                     [width // 2 - self.bottom_text_width, height // 5 * 4 - self.bottom_text_height])

            self.duration -= 1


class BossIntro:
    def __init__(self, boss_name="Boss Intro", duration=1020):
        self.survive_wipe = True  # Should it survive FPS boosting measures
        self.start_duration = duration
        self.duration = duration

        self.boss_name = str_to_list(boss_name)

        self.written_text = ""
        self.particles = []
        self.bar_x_mod = 0
        self.warning_x_mod = -120

        self.end_duration = -BIG_INT

        comms = []
        for i in range(4):
            comms.append(
                {"Sender": "SYS", "Message": str_to_list(write_textline(f"BOSS-INTRO-{random.randint(0, 19)}"))},
            )
        self.comms = UICommunicationLog(comms, [10, 128], speed=3, offset=10)
        # {"Sender": "THR-1", "Message": str_to_list("I AM MAKING MAC AND CHEESE AND NOBODY CAN STOP ME!")}

    def draw(self, WIN, scrolling):
        # Fade in
        if self.duration > self.end_duration:
            # width, height = WIN.get_size()
            width, height = FRAME_MAX_SIZE
            z_mod = FRAME_MAX_SIZE[0]/630

            # Move both bars to the left and right
            base_dist = 32 * z_mod
            bar_height = 3 * z_mod
            bar_spread = 48 * z_mod
            pg.draw.rect(WIN, AMBER, (self.bar_x_mod* z_mod-width, base_dist, width, bar_height ))
            pg.draw.rect(WIN, AMBER, (self.bar_x_mod* z_mod-width, base_dist + bar_spread, width, bar_height ))
            pg.draw.rect(WIN, AMBER, (width-self.bar_x_mod* z_mod, height - base_dist - bar_height * 2 - bar_spread, width, bar_height ))
            pg.draw.rect(WIN, AMBER, (width-self.bar_x_mod* z_mod, height - base_dist - bar_height, width, bar_height ))

            # draw text
            temp_font = create_temp_font_4(height)
            text_sprite = temp_font.render("WARNING", True, AMBER_LIGHT)
            text_width = text_sprite.get_width() + 30 * z_mod
            text_spread = (bar_spread - text_sprite.get_height()) / 2

            for x in range(int(width // text_width * 8)):
                WIN.blit(text_sprite, [
                    (self.warning_x_mod - text_width * x) * z_mod,
                    base_dist+bar_height+text_spread
                ])

            for x in range(int(width // text_width * 8)):
                WIN.blit(text_sprite, [
                    (width - self.warning_x_mod + text_width * x - 120) * z_mod,
                    height - base_dist - bar_height - bar_spread+text_spread
                ])
            self.warning_x_mod += 2

            if 630 > self.bar_x_mod:
                self.bar_x_mod += 4
                if not 630 > self.bar_x_mod:
                    # play noise
                    pass
            else:
                # Write boss name
                if self.duration % 30 == 0:
                    if self.boss_name:
                        self.written_text += self.boss_name[0]
                        self.boss_name.pop(0)
                        if not self.boss_name:
                            self.end_duration = self.duration - 240

                name_sprite = temp_font.render(self.written_text, True, AMBER_LIGHT)
                WIN.blit(name_sprite, [
                    width//2 - name_sprite.get_width()//2,
                    height//2 - name_sprite.get_height()//2
                ])
            # Handles shits
            for i in self.particles:
                i.draw(WIN, scrolling)
            self.comms.act()
            self.comms.draw(WIN, z=z_mod)
            #  * z_mod
            self.duration -= 1


class Music:
    def __init__(self, text, duration=180, color=WHITE, start_delay=180):
        self.survive_wipe = True  # Should it survive FPS boosting measures
        self.start_duration = duration
        self.duration = duration
        self.start_delay = start_delay

        self.text = FONTS["dia"].render(text, True, color)
        self.text_width = self.text.get_width() // 2
        self.text_height = self.text.get_height() // 2

        self.text_alpha = 255

        self.rect = pg.Rect(0, 0, 0, 0)

    def draw(self, WIN, scrolling):
        # Fade in
        if self.duration > 0:
            if self.start_delay == 0:
                width, height = WIN.get_size()

                # Change height of the rects
                if self.duration == self.start_duration:
                    rect_height = height // 10
                else:
                    rect_height = self.rect.height
                if self.duration <= self.start_duration // 3 * 2 and self.rect.height > 1:
                    rect_height -= (height // 5) // (self.duration // 3 * 2)

                self.rect = pg.Rect(0, 0, width, rect_height)

                # Draw the rects
                draw_transparent_rect(WIN, self.rect, BLACK, 175)

                # Draw Text
                if self.duration <= self.start_duration // 3 * 2:
                    self.text_alpha -= 4
                    self.text.set_alpha(self.text_alpha)
                WIN.blit(self.text, [25, 0])

                self.duration -= 1
            else:
                self.start_delay -= 1


class CutsceneSkip:
    def __init__(self, size):
        # This version doesn't fate out
        self.survive_wipe = True  # Should it survive FPS boosting measures
        self.duration = 1
        self.size = size
        self.text = UI_FONT.render("Keep pressing to skip", True, UI_COLOUR_FONT)

    def draw(self, WIN, scrolling):
        # Fade in
        if self.duration > 0:
            y = WIN.get_height() - 10
            pg.draw.rect(WIN, UI_COLOUR_BACKDROP, (0, y, 120, 10))
            pg.draw.rect(WIN, UI_COLOUR_HIGHLIGHT, (0, y, self.size * 2, 10))
            WIN.blit(self.text, [0, y])
            self.duration -= 1


class AfterImage:
    def __init__(self, pos, sprite, duration):
        self.survive_wipe = True
        self.duration = duration
        self.pos = pos
        self.sprite = sprite
        self.width = sprite.get_width()
        self.height = sprite.get_height()

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            drawing_pos = [
                self.pos[0] + scrolling[0] - self.width // 2,
                self.pos[1] + scrolling[1] - self.height // 2
            ]
            WIN.blit(self.sprite, drawing_pos)
            self.duration -= 1


class AfterImageRotated:
    def __init__(self, pos, sprite, duration, angle):
        self.survive_wipe = True
        self.duration = duration
        self.pos = pos
        self.sprite = sprite
        self.width = sprite.get_width()
        self.height = sprite.get_height()
        self.angle = angle
        self.origin = [self.width / 2, self.height / 2]
        # if modified_origin:
        #     self.origin = modified_origin

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            drawing_pos = [
                self.pos[0] + scrolling[0] - self.width // 2,
                self.pos[1] + scrolling[1] - self.height // 2
            ]
            blitRotate(WIN, self.sprite, drawing_pos, self.origin, 180 - self.angle)
            # WIN.blit(self.sprite, drawing_pos)
            self.duration -= 1


class BulletHole:
    def __init__(self, pos):
        self.survive_wipe = False
        self.duration = 6000
        self.pos = pos
        self.sprite = SPRITE_BULLET_HOLES.subsurface((random.randint(0, 3) * 8, random.randint(0, 1) * 8, 8, 8))
        self.width = 8
        self.height = 8

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            drawing_pos = [
                self.pos[0] + scrolling[0] - self.width // 2,
                self.pos[1] + scrolling[1] - self.height // 2
            ]
            WIN.blit(self.sprite, drawing_pos, special_flags=pg.BLEND_RGBA_SUB)
            self.duration -= 1


class SecondPistolParticle:
    def __init__(self, pos, sprite, reloading, reload_time, no_shoot_state, aim_angle):
        self.survive_wipe = True
        self.duration = 1
        self.pos = pos
        self.sprite = sprite
        self.reloading = reloading
        self.reload_time = reload_time
        self.no_shoot_state = no_shoot_state
        self.aim_angle = aim_angle
        if -90 < aim_angle < 90:
            self.aim_angle = aim_angle

    def draw(self, WIN, scrolling):
        if self.duration > 0:
            angle_to_add = 0
            if self.reloading:
                angle_to_add = (360 / self.reload_time) * self.no_shoot_state

            angle_modifier = 40
            if -90 < self.aim_angle < 90:
                angle_modifier = -40

            drawing_pos = [
                self.pos[0] - 9 * math.cos((self.aim_angle + angle_modifier) * math.pi / 180) // 2 + scrolling[0],
                self.pos[1] - 9 * math.sin((self.aim_angle + angle_modifier) * math.pi / 180) // 2 + scrolling[1]
            ]

            self.sprite.get_height() // 2
            if -90 < self.aim_angle < 90:
                blitRotate(WIN, pg.transform.flip(self.sprite, True, True),
                           drawing_pos,
                           [0, 0], 180 - self.aim_angle + angle_to_add)
            else:
                blitRotate(WIN, pg.transform.flip(self.sprite, True, False),
                           drawing_pos, [0, 0], 180 - self.aim_angle + angle_to_add)
            self.duration -= 1


# |Particle Functions|--------------------------------------------------------------------------------------------------
def bloodshed(entities, pos, amount):
    # Just a way to have a certain effect
    for x in range(amount):
        deez_nuts = random.randint(0, 1)
        angle = [0, 180][deez_nuts] + random.randint(-5, 5)
        angle_deviation = [-4, 4][deez_nuts] + random.randint(-2, 2)
        entities["particles"].append(RandomParticle3([pos[0], pos[1]], (255, 0, 0), random.uniform(0.5, 2.5),
                                                     random.randint(10, 20), angle, angle_deviation))


def sparks(entities, pos, bullet_info, angle):
    # bullet_info [duration, radius, speed]
    for x in range(random.randint(int(bullet_info[1] * 0.5 + 1), int(bullet_info[1] * 1.5)) + 1):
        used_angle = angle + 180 + random.randint(-15, 15)
        entities["particles"].append(RandomParticle2([pos[0], pos[1]], (255, 207, 0),
                                                     random.uniform(bullet_info[2] * 0.5, bullet_info[2] * 1.5),
                                                     random.uniform(bullet_info[0] * 0.5, bullet_info[0] * 1.5) * 5 + 5,
                                                     used_angle, size=2))


def sparks_2(entities, pos, angle, colour=WHITE, speed_range=(1, 4), angle_deviation=3, duration_range=(10, 15), size=4
             ):
    for y in range(random.randint(5, 8)):
        entities["particles"].append(RandomParticle2([pos[0], pos[1]],
                                                     colour,
                                                     random.uniform(speed_range[0], speed_range[1]),
                                                     random.randint(duration_range[0], duration_range[1]),
                                                     angle + random.uniform(-angle_deviation, angle_deviation),
                                                     size=size))


def flame_burst(entities, pos, bullet_info, angle, colour_to_use):
    # bullet_info [duration, radius, speed]
    for x in range(random.randint(round(bullet_info[1] * 0.5 + 1), round(bullet_info[1] * 1.5)) * 10):
        entities["particles"].append(FireParticle([pos[0], pos[1]], colour=colour_to_use))


def rain_fall(entities, pos, radius, colour=WATER_NORMAL):
    if len(entities["particles"]) <= 5000:
        for x in range(random.randint(0, 1)):
            true_pos = random_point_in_circle(pos, radius)

            entities["particles"].append(RainParticle([true_pos[0], true_pos[1] - 300], colour=colour))


def random_particle_2_circle(entities, center, speed, duration, number_of_particle, colour=WHITE, size=2, angle_mod=0):
    for particles_to_add in range(360 // number_of_particle):
        entities["particles"].append(RandomParticle2([center[0], center[1]], colour, speed, duration,
                                                     particles_to_add * number_of_particle + angle_mod, size=size))


def random_particle_2_circle_start_offset(entities, center, offset, speed, duration, number_of_particle, colour=WHITE, size=2, angle_mod=0):
    for particles_to_add in range(360 // number_of_particle):
        angle = particles_to_add * number_of_particle + angle_mod
        entities["particles"].append(RandomParticle2(move_with_vel_angle(center, offset, angle), colour, speed, duration,
                                                     angle, size=size))

