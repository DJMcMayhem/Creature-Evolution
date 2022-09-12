import Actor
from PyQt5.QtGui import QPainter, QBrush, QColor

import asyncio
import random
import math

from Food import Food
from Degrees import angle_between
import Brain

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

            # child.cur_velocity = 0
            # invoke(lambda: Prey.set_velocity(child, child.speed), 1)

            self.environment.actors[DumbPrey].append(child)

    def set_velocity(self, new_vel):
        self.cur_velocity = new_vel

    def draw(self, painter: QPainter):
        painter.setBrush(QBrush(QColor(self.color)))
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

        target_x = self.center_x + math.cos(math.radians(self.cur_heading)) * self.speed
        target_y = self.center_y + math.sin(math.radians(self.cur_heading)) * self.speed

        painter.drawLine(self.center_x, self.center_y, target_x, target_y)

        #painter.setBrush(QBrush())
        #painter.setPen(QColor("blue"))
        #painter.drawRoundedRect(
        #    self.center_x - self.vision,
        #    self.center_y - self.vision,
        #    self.vision * 2, self.vision * 2, self.vision * 2, self.vision * 2
        #)


class BrainPrey(Actor.MovingActor):
    WIDTH = 10
    HEIGHT = 10

    def __init__(self, x, y, environment):
        super().__init__(x, y, BrainPrey.WIDTH, BrainPrey.HEIGHT, environment)
        self.cur_heading = random.randint(0, 360)
        self.target_heading = self.cur_heading

        self.speed = 30
        self.angular_speed = 200
        self.vision = 100
        self.energy_level = 500

        self.color = "blue"
        self.eaten = False

        self.cur_velocity = self.speed

        self.invoke_repeating(self.process_brain, 1)
        self.invoke_repeating(self.fast_update, 0.1)

        self.num_inputs = 4
        self.brain = Brain.Brain.from_layers([self.num_inputs, 15, 5, 3], randomize=True, connect_first=True, activation=Brain.relu)

    def process_brain(self):
        inputs = [0 for _ in range(self.num_inputs)]
        nearest, dist = self.environment.get_nearest_actor(self, Food)
        if nearest is not None and dist <= self.vision:
            deg = angle_between(self.center_x, self.center_y, nearest.center_x, nearest.center_y)
            inputs[0] = abs(deg) / 180.0
            inputs[1] = 1 if deg > 0 else -1
            inputs[2] = dist / self.vision
        else:
            inputs[0] = 0
            inputs[1] = 0
            inputs[2] = 0

        inputs[3] = self.energy_level / 1000

        outputs = self.brain.get_output(inputs)
        l_rot, r_rot, target_velocity = outputs

        if l_rot > r_rot:
            rot = max(l_rot, 1.0)
        else:
            rot = -max(r_rot, 1.0)

        self.target_heading = self.cur_heading + (rot * 180.0)

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

        if self.energy_level <= 0:
            self.environment.schedule_remove_actor(self)

        if self.energy_level > 1000:
            self.energy_level -= 500
            child = BrainPrey(self.x, self.y, self.environment)
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
        target_y = self.center_y + math.sin(math.radians(self.cur_heading)) * self.speed

        painter.drawLine(self.center_x, self.center_y, target_x, target_y)

        #painter.setBrush(QBrush())
        #painter.setPen(QColor("blue"))
        #painter.drawRoundedRect(
        #    self.center_x - self.vision,
        #    self.center_y - self.vision,
        #    self.vision * 2, self.vision * 2, self.vision * 2, self.vision * 2
        #)

