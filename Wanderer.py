import Actor
from PyQt5.QtGui import QPainter, QBrush, QColor

import asyncio
import random

from EventLoop import invoke_repeating


class Wanderer(Actor.Actor):
    def __init__(self, x, y, environment):
        super().__init__(x, y, 10, 10, environment)
        self.cur_heading = random.randint(0, 360)
        self.target_heading = self.cur_heading

        self.speed = 30
        self.angular_speed = 180

        self.environment = environment

        self.cur_velocity = self.speed

        invoke_repeating(self.rotate, 1)

    def rotate(self):
        self.target_heading = random.randint(0, 360)

    def draw(self, painter: QPainter):
        painter.setBrush(QBrush(QColor("black")))
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

    def on_overlap(self, other: Actor):
        if type(other) is Wanderer:
            self.environment.actors.remove(self)
