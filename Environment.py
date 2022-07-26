from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush
from PyQt5.QtCore import Qt, pyqtSlot, pyqtProperty, pyqtSignal
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

        # Move and draw at 60 _FPS, but check overlap is more intensive so do that every 100ms
        # This might miss some collisions
        invoke_repeating(self.spawn_actors, 1)
        invoke_repeating(self.update_actors, 1 / 60)
        invoke_repeating(self.check_overlap, 0.1)
        invoke_repeating(self.print_frame_time, 1)

        self.last_update_time = None

        self._frames = 0
        self._fps = 0

    fps_changed = pyqtSignal()
    @pyqtProperty(int, notify=fps_changed)
    def fps(self):
        return self._fps

    actor_count_changed = pyqtSignal()
    @pyqtProperty(int, notify=actor_count_changed)
    def actor_count(self):
        return len(self.actors)

    def print_frame_time(self):
        self._fps = self._frames
        self._frames = 0
        self.fps_changed.emit()

    def paint(self, painter: QPainter):
        for actor in self.actors:
            actor.draw(painter)

    def spawn_actors(self):
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

        self.update()
        self._frames += 1

        self.actor_count_changed.emit()

    def check_overlap(self):
        overlap = []

        for i, actor in enumerate(self.actors):
            for other_actor in self.actors[i + 1:]:
                if actor.overlaps(other_actor):
                    overlap.append((actor, other_actor))

        for a1, a2 in overlap:
            a1.on_overlap(a2)
            a2.on_overlap(a1)

