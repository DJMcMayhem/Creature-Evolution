import Actor
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen


class Food(Actor.Actor):
    WIDTH = 10
    HEIGHT = 10

    def __init__(self, x, y, environment):
        super().__init__(x, y, Food.WIDTH, Food.HEIGHT, environment)

        # When food gets eaten, instantly mark it as deleted so that no other actor can eat it
        self.eaten = False
        self.color = "green"

    def draw(self, painter: QPainter):
        painter.setBrush(QBrush(QColor(self.color)))
        painter.setPen(QPen())
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
