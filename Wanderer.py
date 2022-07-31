import Actor
from PyQt5.QtGui import QPainter, QBrush, QColor

import asyncio
import random


class Wanderer(Actor.MovingActor):
    WIDTH = 10
    HEIGHT = 10

    def __init__(self, x, y, environment):
        super().__init__(x, y, Wanderer.WIDTH, Wanderer.HEIGHT, environment)
        self.cur_heading = random.randint(0, 360)
        self.target_heading = self.cur_heading

        self.speed = 30
        self.angular_speed = 180

        self.cur_velocity = self.speed

        self.invoke_repeating(self.rotate, 1)
        self.invoke_repeating(self.check_collision, 0.2)

    def rotate(self):
        self.target_heading = random.randint(0, 360)

    def check_collision(self):
        nearest, dist = self.environment.get_nearest_actor(self, Wanderer)

        if nearest is not None and dist == 0:
            self.environment.schedule_remove_actor(self)
            self.environment.schedule_remove_actor(nearest)
            self.destroy()
            nearest.destroy()

    def draw(self, painter: QPainter):
        painter.setBrush(QBrush(QColor("black")))
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

