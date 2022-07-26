from __future__ import annotations

import abc
from PyQt5.QtGui import QPainter

from math import sin, cos, radians


class Actor(abc.ABC):
    def __init__(self, x, y, width, height, environment):
        self.environment = environment
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.cur_heading = 0
        self.cur_velocity = 0

    @abc.abstractmethod
    def draw(self, painter: QPainter):
        raise NotImplementedError

    def update(self, delta_time: float):
        delta_y = self.cur_velocity * delta_time * sin(radians(self.cur_heading))
        delta_x = self.cur_velocity * delta_time * cos(radians(self.cur_heading))

        self.x += delta_x
        self.y += delta_y

        self.clamp()

    def overlaps(self, other: Actor) -> bool:
        return (self.left < other.right and self.right > other.left and
                self.top < other.bottom and self.bottom > other.top)

    def on_overlap(self, other: Actor):
        pass

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.width

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.height

    def clamp(self):
        if self.x < 0:
            self.x = 0

        if self.x + self.width > self.environment.width():
            self.x = self.environment.width() - self.width

        if self.y < 0:
            self.y = 0

        if self.y + self.height > self.environment.height():
            self.y = self.environment.height() - self.height
