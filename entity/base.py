from abc import ABC, abstractmethod

from pygame import Surface

class Entity(ABC):

    def __init__(self, x: float, y: float):
        """
        Initialize the Entity.
        :param x: Float coordinate representing the center/position on the X axis
        :param y: Float coordinate representing the center/position on the Y axis
        """
        self.x = x
        self.y = y
        self.z_index = 0
        self.layer = None

    def event(self, event):
        pass

    def update(self):
        pass

    @abstractmethod
    def paint(self, surface: Surface):
        pass

