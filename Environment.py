from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtQuick import QQuickPaintedItem

from Wanderer import Wanderer

import asyncio
import random


class Environment(QQuickPaintedItem):
    def __init__(self, parent):
        super().__init__()

        self.actors = []

        asyncio.create_task(self.run())

    def paint(self, painter: QPainter):
        for actor in self.actors:
            actor.draw(painter)

    async def check_overlaps(self):
        while True:
            overlappers = []

            for i, actor in enumerate(self.actors):
                for other_actor in self.actors[i+1:]:
                    if actor.overlaps(other_actor):
                        overlappers.append(actor)
                        overlappers.append(other_actor)

            for actor in overlappers:
                self.actors.remove(actor)

            await asyncio.sleep(0.1)

    async def run(self):
        asyncio.create_task(self.check_overlaps())

        while True:
            if len(self.actors) < 20:
                x = random.randint(0, self.width())
                y = random.randint(0, self.height())
                self.actors.append(Wanderer(x, y, self))

            await asyncio.sleep(1)
