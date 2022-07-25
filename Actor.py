import abc
from PyQt5.QtGui import QPainter

import asyncio


class Actor(abc.ABC):
    def __init__(self, x, y, width, height, environment):
        self.environment = environment
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        asyncio.create_task(self.run())

    @abc.abstractmethod
    def draw(self, painter: QPainter):
        raise NotImplementedError

    @abc.abstractmethod
    async def run(self):
        raise NotImplementedError

    def overlaps(self, other: "Actor") -> bool:
        """
        if (RectA.X1 < RectB.X2 && RectA.X2 > RectB.X1 &&
            RectA.Y1 > RectB.Y2 && RectA.Y2 < RectB.Y1)
        """
        return (self.left < other.right and self.right > other.left and
                self.top < other.bottom and self.bottom > other.top)

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
