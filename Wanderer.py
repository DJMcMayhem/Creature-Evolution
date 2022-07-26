import Actor
from PyQt5.QtGui import QPainter, QBrush, QColor

import asyncio
import random


class Wanderer(Actor.Actor):
    directions = ["N", "E", "S", "W"]

    def __init__(self, x, y, environment):
        super().__init__(x, y, 10, 10, environment)
        self.cur_direction = "N"
        self.speed = 30

        self.environment = environment

        self.elapsed_time = 0.0
        self.turn_time = 2.0

    async def run(self):
        asyncio.create_task(self.rotate())

        while True:
            delta_time = 0.1

            if self.cur_direction == "N":
                self.y -= self.speed * delta_time
            if self.cur_direction == "S":
                self.y += self.speed * delta_time
            if self.cur_direction == "E":
                self.x += self.speed * delta_time
            if self.cur_direction == "W":
                self.x -= self.speed * delta_time

            self.environment.update()

            self.clamp()

            await asyncio.sleep(delta_time)

    async def rotate(self):
        while True:
            self.cur_direction = random.choice(Wanderer.directions)
            await asyncio.sleep(1)

    def draw(self, painter: QPainter):
        painter.setBrush(QBrush(QColor("black")))
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
