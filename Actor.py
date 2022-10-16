from __future__ import annotations

import abc
import asyncio
from abc import ABC
from PyQt5.QtGui import QPainter
from math import sin, cos, radians, sqrt
from Degrees import rotate_towards
from EventLoop import invoke_repeating


class Actor(abc.ABC):
    def __init__(self, x, y, width, height, environment):
        self.environment = environment
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.tasks = []

    @abc.abstractmethod
    def draw(self, painter: QPainter):
        raise NotImplementedError

    def invoke_repeating(self, func, time):
        self.tasks.append(invoke_repeating(func, time))

    def update(self, delta_time: float):
        pass

    def overlaps(self, other: Actor) -> bool:
        return (self.left < other.right and self.right > other.left and
                self.top < other.bottom and self.bottom > other.top)

    def edge_distance(self, other: Actor) -> float:
        x_dist = max(0, abs(self.center_x - other.center_x) - (self.width + other.width) / 2)
        y_dist = max(0, abs(self.center_y - other.center_y) - (self.height + other.height) / 2)

        return sqrt(x_dist ** 2 + y_dist ** 2)

    def destroy(self):
        for task in self.tasks:
            task.cancel()

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

    @property
    def center_x(self):
        return self.x + self.width / 2

    @property
    def center_y(self):
        return self.y + self.height / 2

    def clamp(self):
        if self.x < 0:
            self.x = 0

        if self.x + self.width > self.environment.width():
            self.x = self.environment.width() - self.width

        if self.y < 0:
            self.y = 0

        if self.y + self.height > self.environment.height():
            self.y = self.environment.height() - self.height


class MovingActor(Actor, ABC):
    def __init__(self, x, y, width, height, environment):
        super().__init__(x, y, width, height, environment)

        self.cur_heading = 0
        self.target_heading = 0
        self.cur_velocity = 0

        # Degrees/second
        self.angular_speed = 0

    def update(self, delta_time: float):
        if self.cur_heading != self.target_heading:
            self.cur_heading = rotate_towards(self.cur_heading, self.target_heading, self.angular_speed * delta_time)

        delta_y = self.cur_velocity * delta_time * sin(radians(self.cur_heading))
        delta_x = self.cur_velocity * delta_time * cos(radians(self.cur_heading))

        self.x += delta_x
        self.y -= delta_y

        self.clamp()

