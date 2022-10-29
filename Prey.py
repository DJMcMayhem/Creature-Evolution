import Actor
from PyQt5.QtGui import QPainter, QBrush, QColor

import asyncio
import random
import math
import numpy as np

from Food import Food
from Degrees import angle_between
import Brain
from RayCaster import RayCaster

from EventLoop import invoke


class DumbPrey(Actor.MovingActor):
    WIDTH = 10
    HEIGHT = 10

    def __init__(self, x, y, environment):
        super().__init__(x, y, DumbPrey.WIDTH, DumbPrey.HEIGHT, environment)
        self.cur_heading = random.randint(0, 360)
        self.target_heading = self.cur_heading

        self.speed = 30
        self.angular_speed = 200
        self.vision = 100
        self.energy_level = 500

        self.color = "blue"
        self.eaten = False

        self.cur_velocity = self.speed

        self.invoke_repeating(self.pick_target, 1)
        self.invoke_repeating(self.fast_update, 0.1)
        self.target_food = None

    def pick_target(self):
        nearest, dist = self.environment.get_nearest_actor(self, Food)
        if nearest is not None and dist <= self.vision:
            deg = angle_between(self.center_x, self.center_y, nearest.center_x, nearest.center_y)
            self.target_food = nearest
            self.target_heading = deg
        else:
            self.target_heading = random.randint(0, 360)

    def fast_update(self):
        # Has the food been eaten?
        if self.target_food is not None and not self.target_food.eaten and self.edge_distance(self.target_food) == 0:
            self.environment.schedule_remove_actor(self.target_food)
            self.energy_level += 500
            self.target_food.eaten = True
            self.target_food = None

            # self.cur_velocity = 0
            # invoke(lambda: self.set_velocity(self.speed), 1)

        if self.target_food is not None:
            deg = angle_between(self.center_x, self.center_y, self.target_food.center_x, self.target_food.center_y)
            self.target_heading = deg

        # How much energy have we spent?
        size = self.width * self.height / 100
        self.energy_level -= self.cur_velocity * 0.1 * size

        if self.energy_level <= 0:
            self.environment.schedule_remove_actor(self)

        if self.energy_level > 1000:
            self.energy_level -= 500
            child = DumbPrey(self.x, self.y, self.environment)
            child.color = self.color
            child.speed = self.speed * random.uniform(0.90, 1.10)
            child.vision = self.vision * random.uniform(0.90, 1.10)
            child.angular_speed = self.angular_speed * random.uniform(0.90, 1.10)
            child.width = self.width * random.uniform(0.90, 1.10)
            child.height = child.width

            self.environment.actors[DumbPrey].append(child)

    def set_velocity(self, new_vel):
        self.cur_velocity = new_vel

    def draw(self, painter: QPainter):
        painter.setBrush(QBrush(QColor(self.color)))
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

        target_x = self.center_x + math.cos(math.radians(self.cur_heading)) * self.speed
        target_y = self.center_y - math.sin(math.radians(self.cur_heading)) * self.speed

        painter.drawLine(self.center_x, self.center_y, target_x, target_y)


class BrainPrey(Actor.MovingActor):
    WIDTH = 10
    HEIGHT = 10

    def __init__(self, x, y, environment):
        super().__init__(x, y, BrainPrey.WIDTH, BrainPrey.HEIGHT, environment)
        self.ray_caster = RayCaster(self, 7, 60, 100)

        self.cur_heading = random.randint(0, 360)
        self.target_heading = self.cur_heading

        self.speed = 30
        self.angular_speed = 200
        self.vision = 100
        self.energy_level = 500

        self.color = "blue"
        self.eaten = False

        self.cur_velocity = 0

        self.invoke_repeating(self.process_brain, 1)
        self.invoke_repeating(self.fast_update, 0.1)

        self.num_inputs = self.ray_caster.num_eyes
        self.num_outputs = 4
        self.brain = Brain.Brain.from_layers([self.num_inputs, 10, self.num_outputs],
                                             randomize_amt=0.15, connect_first=True, activation=Brain.relu)

    def process_brain(self):
        inputs = self.ray_caster.get_inputs()
        speed_output, l_rot, r_rot, angular_velocity = self.brain.get_output(inputs)

        self.cur_velocity = np.tanh(np.maximum(0, speed_output)) * self.speed
        rot_amount = np.clip(l_rot - r_rot, -1, 1)
        self.target_heading += rot_amount * self.angular_speed
        #rot_amount = np.clip(angular_velocity, -self.angular_speed, self.angular_speed)

        #if r_rot > l_rot:
        #    rot_amount = 0 - rot_amount

        #self.target_heading += rot_amount

    def fast_update(self):
        # Has the food been eaten?
        target_food = None
        nearest, dist = self.environment.get_nearest_actor(self, Food)
        if nearest is not None and dist <= self.vision:
            target_food = nearest

        if target_food is not None and not target_food.eaten and dist == 0:
            self.environment.schedule_remove_actor(target_food)
            self.energy_level += 500
            target_food.eaten = True

        # How much energy have we spent?
        size = self.width * self.height / 100
        self.energy_level -= self.cur_velocity * 0.1 * size
        self.energy_level -= 1

        if self.energy_level <= 0:
            self.environment.schedule_remove_actor(self)

        if self.energy_level > 1000:
            self.energy_level -= 500
            child = BrainPrey(self.x, self.y, self.environment)
            child.target_heading = self.target_heading
            child.cur_heading = self.cur_heading

            if self.color == "blue":
                mutation_strength = 0.10
            else:
                mutation_strength = 0
            child.color = self.color
            child.brain = self.brain.mutate(mutation_strength, 0.15)

            self.environment.actors[BrainPrey].append(child)

    def set_velocity(self, new_vel):
        self.cur_velocity = new_vel

    def draw(self, painter: QPainter):
        painter.setBrush(QBrush(QColor(self.color)))
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

        target_x = self.center_x + math.cos(math.radians(self.cur_heading)) * self.speed
        target_y = self.center_y - math.sin(math.radians(self.cur_heading)) * self.speed

        painter.drawLine(self.center_x, self.center_y, target_x, target_y)

        # self.ray_caster.draw(painter)

        #painter.setBrush(QBrush())
        #painter.setPen(QColor("blue"))
        #painter.drawRoundedRect(
        #    self.center_x - self.vision,
        #    self.center_y - self.vision,
        #    self.vision * 2, self.vision * 2, self.vision * 2, self.vision * 2
        #)

