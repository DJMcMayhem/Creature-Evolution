from PyQt5.QtGui import QPainter

import numpy as np

import math

import Actor


class RayCaster:
    def __init__(self, parent_actor: Actor.MovingActor, num_eyes, fov, vision_distance):
        self.parent_actor = parent_actor

        self.num_eyes = num_eyes
        self.fov = fov
        self.vision_distance = vision_distance

        # The fencepost problem: If there are n eyes, then the angle between each eye is total_width / (n - 1)
        betweens = self.num_eyes - 1
        center = betweens / 2

        if num_eyes == 1:
            self.eye_angles = [center]
        else:
            self.eye_angles = [(center - i) * (self.fov / betweens) for i in range(self.num_eyes)]

        self.debug_lines = []

    def get_inputs(self):
        closests = np.repeat(math.inf, self.num_eyes)

        self.debug_lines = []

        for actor in self.parent_actor.environment.actors_within_dist(self.parent_actor, self.vision_distance):
            origin = np.array([self.parent_actor.center_x, self.parent_actor.center_y])

            corner_vectors = [
                np.array([actor.left, actor.top]) - origin,
                np.array([actor.right, actor.top]) - origin,
                np.array([actor.left, actor.bottom]) - origin,
                np.array([actor.right, actor.bottom]) - origin
            ]

            for i, d_angle in enumerate(self.eye_angles):
                angle = self.parent_actor.cur_heading + d_angle

                off_x = math.cos(math.radians(angle)) * self.vision_distance
                off_y = -math.sin(math.radians(angle)) * self.vision_distance

                ray = np.array([off_x, off_y])

                directions = list(np.unique(np.sign(np.cross(ray, corner_vectors))))

                # if all corners are to our left, none of the other rays might hit this actor
                if directions == [-1.0]:
                    break

                # If all corners are to our right, this ray doesn't hit this actor, but one of the next ones might
                if directions == [1.0]:
                    continue

                # Otherwise, this ray must have hit this actor
                dist = np.hypot(*origin - np.array([actor.center_x, actor.center_y]))
                if dist < closests[i]:
                    closests[i] = dist

        return closests / self.vision_distance

    def draw(self, painter: QPainter):
        inputs = self.get_inputs()

        for i, d_angle in enumerate(self.eye_angles):
            angle = self.parent_actor.cur_heading + d_angle

            if inputs[i] == math.inf:
                multiplier = 1.0
            else:
                multiplier = inputs[i]

            target_x = self.parent_actor.center_x + math.cos(math.radians(angle)) * self.vision_distance * multiplier
            target_y = self.parent_actor.center_y - math.sin(math.radians(angle)) * self.vision_distance * multiplier

            painter.drawLine(self.parent_actor.center_x, self.parent_actor.center_y, target_x, target_y)

        for p1, p2 in self.debug_lines:
            painter.drawLine(*p1, *p2)

