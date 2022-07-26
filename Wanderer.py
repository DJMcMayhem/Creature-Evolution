import Actor
from PyQt5.QtGui import QPainter, QBrush, QColor

import asyncio
import random

from EventLoop import invoke_repeating


class Wanderer(Actor.Actor):
    directions = ["N", "E", "S", "W"]

    def __init__(self, x, y, environment):
        super().__init__(x, y, 10, 10, environment)
        self.cur_direction = "N"
        self.speed = 30

        self.environment = environment

        self.elapsed_time = 0.0
        self.turn_time = 2.0

        self.cur_velocity = self.speed

        invoke_repeating(self.rotate, 1)

    def rotate(self):
        self.cur_heading = random.randint(0, 360)

    def draw(self, painter: QPainter):
        painter.setBrush(QBrush(QColor("black")))
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

    def on_overlap(self, other: Actor):
        if type(other) is Wanderer:
            self.environment.actors.remove(self)
