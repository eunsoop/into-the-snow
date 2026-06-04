from abc import abstractmethod, ABC
from typing import final

from pygame import Surface


class Scene(ABC):
    def __init__(self):
        self.game = None

    def __set_game__(self, game): self.game = game

    @final
    def get_game(self): return self.game

    @abstractmethod
    def event(self, event): pass
    @abstractmethod
    def paint(self, surface: Surface): pass


class Layer(ABC):
    def __init__(self):
        self.game = None

    @final
    def __set_game__(self, game): self.game = game
    @final
    def get_game(self): return self.game

    @abstractmethod
    def event(self, event): pass
    @abstractmethod
    def paint(self, surface: Surface): pass


class LayeredScene(Scene):
    def __init__(self, layers: list[Layer] = []):
        super().__init__()
        self.layers = layers

    def __set_game__(self, game):
        super().__set_game__(game)
        for layer in self.layers:
            layer.__set_game__(game)

    def add_layer(self, layer: Layer):
        layer.__set_game__(self.game)
        self.layers.append(layer)

    def event(self, event):
        for layer in self.layers: layer.event(event)

    def paint(self, surface: Surface):
        for layer in self.layers: layer.paint(surface)