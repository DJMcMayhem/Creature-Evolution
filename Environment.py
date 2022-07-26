from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtQuick import QQuickPaintedItem

from Wanderer import Wanderer

from EventLoop import invoke_repeating

import asyncio
import random
import time


class Environment(QQuickPaintedItem):
    def __init__(self, parent):
        super().__init__()

        self.actors = []

        # asyncio.create_task(self.run())
        invoke_repeating(self.spawn_creatures, 1)
        invoke_repeating(self.update_actors, 1 / 60)
        invoke_repeating(self.print_frame_time, 1)

        self.last_frame = 0

        self.last_update_time = None

    def print_frame_time(self):
        print(self.last_frame)

    def paint(self, painter: QPainter):
        for actor in self.actors:
            actor.draw(painter)

    def spawn_creatures(self):
        if len(self.actors) < 20:
            x = random.randint(0, self.width())
            y = random.randint(0, self.height())
            self.actors.append(Wanderer(x, y, self))

    def update_actors(self):
        t = time.time()
        if self.last_update_time is None:
            self.last_update_time = t

        time_delta = t - self.last_update_time
        self.last_update_time = t

        for actor in self.actors:
            actor.update(time_delta)

        # Check for overlap
        overlap = []

        for i, actor in enumerate(self.actors):
            for other_actor in self.actors[i + 1:]:
                if actor.overlaps(other_actor):
                    overlap.append((actor, other_actor))

        for a1, a2 in overlap:
            a1.on_overlap(a2)
            a2.on_overlap(a1)

        self.update()

        self.last_frame = time.time() - t
