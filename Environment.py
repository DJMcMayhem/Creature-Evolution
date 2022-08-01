from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush
from PyQt5.QtCore import Qt, pyqtSlot, pyqtProperty, pyqtSignal
from PyQt5.QtQuick import QQuickPaintedItem

import Actor
from Wanderer import Wanderer
from Food import Food
from Prey import Prey
from Predator import Predator
from EventLoop import invoke_repeating, invoke

import asyncio
import random
import time
import typing
import math


class Environment(QQuickPaintedItem):
    def __init__(self, parent):
        super().__init__()

        self.actors: typing.Dict[type, typing.List[Actor.Actor]] = {
            Wanderer: [],
            Prey: [],
            Predator: [],
            Food: []
        }

        # Move and draw at 60 _FPS, but check overlap is more intensive so do that every 100ms
        # This might miss some collisions
        invoke_repeating(lambda: self.spawn_actors(Food, 2), 0.5)
        invoke_repeating(self.update_actors, 1 / 60)
        invoke_repeating(self.update_frame_time, 1)
        invoke(self.spawn_initial, 1)

        self.last_update_time = None

        self._frames = 0
        self._fps = 0

        self.delete_actors: typing.Set[Actor.Actor] = set()

    @pyqtSlot(int, int)
    def on_clicked(self, x, y):
        for actor_list in self.actors.values():
            for actor in actor_list:
                if actor.left <= x <= actor.right and actor.top <= y <= actor.bottom:
                    print(actor)
                    return

        print("No actor found")

    def spawn_initial(self):
        self.spawn_actors(Prey, 10)
        self.spawn_actors(Food, 20)
        self.spawn_actors(Predator, 5)

    fps_changed = pyqtSignal()
    @pyqtProperty(int, notify=fps_changed)
    def fps(self):
        return self._fps

    prey_count_changed = pyqtSignal()
    @pyqtProperty(int, notify=prey_count_changed)
    def prey_count(self):
        return len(self.actors[Prey])

    predator_count_changed = pyqtSignal()
    @pyqtProperty(int, notify=predator_count_changed)
    def predator_count(self):
        return len(self.actors[Predator])

    def schedule_remove_actor(self, actor):
        self.delete_actors.add(actor)

    def update_frame_time(self):
        self._fps = self._frames
        self._frames = 0
        self.fps_changed.emit()

    def paint(self, painter: QPainter):
        self._frames += 1
        for actor_type_list in self.actors.values():
            for actor in actor_type_list:
                actor.draw(painter)

    def spawn_actors(self, actor_type, n):
        for i in range(n):
            x = random.randint(0, self.width() - actor_type.WIDTH)
            y = random.randint(0, self.height() - actor_type.HEIGHT)
            self.actors[actor_type].append(actor_type(x, y, self))

    def update_actors(self):
        t = time.time()

        for actor in self.delete_actors:
            # This is necessary because of async, deleted Actors might still call things and reference the environment
            try:
                self.actors[type(actor)].remove(actor)
                actor.destroy()
            except ValueError:
                print(actor)

        self.delete_actors = set()

        if self.last_update_time is None:
            self.last_update_time = t

        time_delta = t - self.last_update_time
        self.last_update_time = t

        for actor_type_list in self.actors.values():
            for actor in actor_type_list:
                actor.update(time_delta)

        self.update()

        self.predator_count_changed.emit()
        self.prey_count_changed.emit()

    """
    def check_overlap_naive(self):
        overlap = []

        for i, actor in enumerate(self.actors):
            for other_actor in self.actors[i + 1:]:
                if actor.overlaps(other_actor):
                    overlap.append((actor, other_actor))

        for a1, a2 in overlap:
            a1.on_overlap(a2)
            a2.on_overlap(a1)
    """

    def get_nearest_actor(self, actor: Actor.Actor, actor_type: type) -> typing.Tuple[Actor.Actor, float]:
        closest_dist = math.inf
        closest_actor = None
        for other in self.actors[actor_type]:
            if other is actor or other in self.delete_actors:
                continue

            if (dist := actor.edge_distance(other)) < closest_dist:
                closest_dist = dist
                closest_actor = other

        return closest_actor, closest_dist
