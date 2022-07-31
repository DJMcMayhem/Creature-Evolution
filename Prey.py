import Actor
from PyQt5.QtGui import QPainter, QBrush, QColor

import asyncio
import random
import math

from Food import Food
from Degrees import angle_between

from EventLoop import invoke


class Prey(Actor.MovingActor):
    WIDTH = 10
    HEIGHT = 10

    def __init__(self, x, y, environment):
        super().__init__(x, y, Prey.WIDTH, Prey.HEIGHT, environment)
        self.cur_heading = random.randint(0, 360)
        self.target_heading = self.cur_heading

        self.speed = 30
        self.angular_speed = 360
        self.vision = 100
        self.energy_level = 500

        self.color = "blue"

        self.cur_velocity = self.speed

        self.invoke_repeating(self.pick_target, 1)
        self.invoke_repeating(self.fast_update, 0.1)
        self.target_food = None

    def pick_target(self):
        nearest, dist = self.environment.get_nearest_actor(self, Food)
        if nearest is not None and dist <= self.vision:
            deg = angle_between(self.center_x, self.center_y, nearest.center_x, nearest.center_y)
            self.target_food = nearest
            self.target_heading = deg
        else:
            self.target_heading = random.randint(0, 360)

    def fast_update(self):
        # Has the food been eaten?
        if self.target_food is not None and not self.target_food.eaten and self.edge_distance(self.target_food) == 0:
            self.environment.schedule_remove_actor(self.target_food)
            self.energy_level += 500
            self.target_food.eaten = True
            self.target_food = None
            self.cur_velocity = 0

            invoke(lambda: self.set_velocity(self.speed), 1)

        # How much energy have we spent?
        self.energy_level -= self.cur_velocity * 0.1

        if self.energy_level <= 0:
            self.environment.schedule_remove_actor(self)

        if self.energy_level > 1000:
            self.energy_level -= 500
            child = Prey(self.x, self.y, self.environment)
            child.cur_velocity = 0
            child.color = self.color
            invoke(lambda: Prey.set_velocity(child, child.speed), 1)

            self.environment.actors[Prey].append(child)

    def set_velocity(self, new_vel):
        self.cur_velocity = new_vel

    def draw(self, painter: QPainter):
        painter.setBrush(QBrush(QColor(self.color)))
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

        # target_x = self.center_x + math.cos(math.radians(self.cur_heading)) * self.speed
        # target_y = self.center_y + math.sin(math.radians(self.cur_heading)) * self.speed

        # painter.drawLine(self.center_x, self.center_y, target_x, target_y)

        # painter.setBrush(QBrush())
        # painter.setPen(QColor("blue"))
        # painter.drawRoundedRect(
        #     self.center_x - self.vision,
        #     self.center_y - self.vision,
        #     self.vision * 2, self.vision * 2, self.vision * 2, self.vision * 2
        # )

