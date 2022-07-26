import Actor
from PyQt5.QtGui import QPainter, QBrush, QColor

import asyncio
import random
import math

from Prey import DumbPrey
from Degrees import angle_between


class Predator(Actor.MovingActor):
    WIDTH = 10
    HEIGHT = 10

    def __init__(self, x, y, environment):
        super().__init__(x, y, Predator.WIDTH, Predator.HEIGHT, environment)
        self.cur_heading = random.randint(0, 360)
        self.target_heading = self.cur_heading

        self.speed = 50
        self.wander_speed = self.speed * 0.5
        self.angular_speed = 100
        self.vision = 100
        self.energy_level = 500

        self.color = "red"

        self.cur_velocity = self.speed

        self.invoke_repeating(self.pick_target, 1)
        self.invoke_repeating(self.fast_update, 0.1)
        self.target_prey = None
        self.hungry = True

    def get_hungry(self):
        self.hungry = True

    def pick_target(self):
        if not self.hungry:
            self.target_prey = None
            return

        nearest, dist = self.environment.get_nearest_actor(self, DumbPrey)
        if nearest is not None and dist <= self.vision:
            deg = angle_between(self.center_x, self.center_y, nearest.center_x, nearest.center_y)
            self.target_prey = nearest
            self.target_heading = deg
        else:
            self.target_heading = random.randint(0, 360)

    def fast_update(self):
        # Has the food been eaten?
        if self.target_prey is not None and not self.target_prey.eaten:
            if self.edge_distance(self.target_prey) == 0:
                self.environment.schedule_remove_actor(self.target_prey)
                # self.energy_level += self.target_prey.energy_level * 0.8
                self.energy_level += 500
                self.target_prey.eaten = True
                self.target_prey = None

                self.cur_velocity = 0
                # self.hungry = False
                self.invoke(lambda: self.set_velocity(self.wander_speed), 1)
                # invoke(self.get_hungry, 2)
            else:
                deg = angle_between(self.center_x, self.center_y, self.target_prey.center_x, self.target_prey.center_y)
                self.target_heading = deg
                self.cur_velocity = self.speed
        else:
            self.cur_velocity = self.wander_speed

        # How much energy have we spent?
        size = self.width * self.height / 100
        self.energy_level -= self.cur_velocity * 0.1 * size

        if self.energy_level <= 0:
            self.environment.schedule_remove_actor(self)

        if self.energy_level > 1000:
            self.energy_level -= 500
            child = Predator(self.x, self.y, self.environment)
            child.color = self.color
            child.speed = self.speed * random.uniform(0.90, 1.10)
            child.vision = self.vision * random.uniform(0.90, 1.10)
            child.angular_speed = self.angular_speed * random.uniform(0.90, 1.10)
            child.width = self.width * random.uniform(0.90, 1.10)
            child.height = child.width

            child.cur_velocity = 0
            self.invoke(lambda: Predator.set_velocity(child, child.speed), 1)

            self.environment.actors[Predator].append(child)

    def set_velocity(self, new_vel):
        self.cur_velocity = new_vel

    def draw(self, painter: QPainter):
        painter.setBrush(QBrush(QColor(self.color)))
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

        target_x = self.center_x + math.cos(math.radians(self.cur_heading)) * self.speed
        target_y = self.center_y - math.sin(math.radians(self.cur_heading)) * self.speed

        painter.drawLine(self.center_x, self.center_y, target_x, target_y)

        #painter.setBrush(QBrush())
        #painter.setPen(QColor("red"))
        #painter.drawRoundedRect(
        #    self.center_x - self.vision,
        #    self.center_y - self.vision,
        #    self.vision * 2, self.vision * 2, self.vision * 2, self.vision * 2
        #)

