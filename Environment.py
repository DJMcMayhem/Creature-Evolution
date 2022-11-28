from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush
from PyQt5.QtCore import Qt, pyqtSlot, pyqtProperty, pyqtSignal
from PyQt5.QtQuick import QQuickPaintedItem

import Actor
from Wanderer import Wanderer
from Food import Food
from Prey import DumbPrey, BrainPrey
from RayCaster import RayCaster
from Predator import Predator
import EventLoop

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
            DumbPrey: [],
            BrainPrey: [],
            Predator: [],
            RayCaster: [],
            Food: []
        }

        self.event_loop = EventLoop.SynchronousEventLoop()
        # Move and draw at 60 _FPS, but check overlap is more intensive so do that every 100ms
        # This might miss some collisions
        EventLoop.invoke_repeating(self.update_actors, 1 / 60)

        # self.event_loop.invoke_repeating(lambda: self.spawn_actors(Food, 2), 0.5)
        self.event_loop.invoke_repeating(self.update_frame_time, 1)
        self.event_loop.invoke(self.spawn_initial, 1)

        self.last_update_time = None

        self._frames = 0
        self._fps = 0
        self._game_time = 0

        self.delete_actors: typing.Set[Actor.Actor] = set()

        self.num_chunks = 10

        self.chunk_list = [[[] for _ in range(self.num_chunks)] for _ in range(self.num_chunks)]

    @property
    def chunk_size(self):
        return int(self.width() / self.num_chunks)

    gameTimeChanged = pyqtSignal()
    @pyqtProperty(float, notify=gameTimeChanged)
    def game_time(self):
        return self._game_time

    @pyqtSlot(int, int)
    def on_clicked(self, x, y):
        food = Food(x, y, self)
        self.actors[Food].append(food)

    def spawn_initial(self):
        self.spawn_actors(BrainPrey, 20)
        self.spawn_actors(Food, 20)
        #self.spawn_actors(Predator, 2)

    fps_changed = pyqtSignal()
    @pyqtProperty(int, notify=fps_changed)
    def fps(self):
        return self._fps

    prey_count_changed = pyqtSignal()
    @pyqtProperty(int, notify=prey_count_changed)
    def prey_count(self):
        return len(self.actors[DumbPrey]) + len(self.actors[BrainPrey])

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

    def draw_chunks(self, painter: QPainter):
        for x in range(0, self.num_chunks):
            painter.drawLine(x * self.chunk_size, 0, x * self.chunk_size, int(self.height()))

        for y in range(0, self.num_chunks):
            painter.drawLine(0, y * self.chunk_size, int(self.width()), y * self.chunk_size)

    def spawn_actors(self, actor_type, n):
        for i in range(n):
            x = random.randint(0, self.width() - actor_type.WIDTH)
            y = random.randint(0, self.height() - actor_type.HEIGHT)
            self.actors[actor_type].append(actor_type(x, y, self))

    def actors_within_dist(self, actor, dist, actor_types=None):
        actor_chunk_x = int(actor.center_x / self.chunk_size)
        actor_chunk_y = int(actor.center_y / self.chunk_size)

        chunks_away = int(dist / self.chunk_size) + 1

        for d_x in range(-chunks_away, chunks_away + 1):
            for d_y in range(-chunks_away, chunks_away + 1):
                x, y = actor_chunk_x + d_x, actor_chunk_y + d_y

                if not -1 < x < self.num_chunks:
                    continue

                if not -1 < y < self.num_chunks:
                    continue

                for other_actor in self.chunk_list[x][y]:
                    if other_actor is actor:
                        continue

                    if actor_types is None or type(other_actor) in actor_types:
                        if actor.edge_distance(other_actor) < dist:
                            yield other_actor

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

        time_delta = 1/60
        self.last_update_time = t
        self.event_loop.update(time_delta)

        self._game_time += time_delta
        self.gameTimeChanged.emit()

        # Reset the chunk list
        self.chunk_list = [[[] for _ in range(self.num_chunks)] for _ in range(self.num_chunks)]

        for actor_type_list in self.actors.values():
            for actor in actor_type_list:
                x, y = int(actor.center_x / self.chunk_size), int(actor.center_y / self.chunk_size)

                self.chunk_list[x][y].append(actor)

        for actor_type_list in self.actors.values():
            for actor in actor_type_list:
                actor.update(time_delta)

        self.update()

        self.predator_count_changed.emit()
        self.prey_count_changed.emit()

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
