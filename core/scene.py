import pygame
from abc import abstractmethod, ABC
from typing import final
from pygame import Surface


class Scene(ABC):
    def __init__(self):
        self.game = None

    def __set_game__(self, game):
        self.game = game

    @final
    def get_game(self):
        return self.game

    @abstractmethod
    def event(self, event: pygame.event.Event):
        pass

    @abstractmethod
    def paint(self, surface: Surface):
        pass


class LayeredScene(Scene):
    def __init__(self, layers: list = None):
        super().__init__()
        self.layers = layers if layers is not None else []
        self.effectors = []

    def __set_game__(self, game):
        super().__set_game__(game)
        for layer in self.layers:
            layer.__set_game__(game)

    def add_layer(self, layer):
        layer.__set_game__(self.game)
        self.layers.append(layer)

    def add_layers(self, layers: list):
        for layer in layers:
            self.add_layer(layer)

    def add_effector(self):
        pass

    def remove_layer(self, layer):
        if layer in self.layers:
            self.layers.remove(layer)
            layer.__set_game__(None)

    def replace_layer(self, old_layer, new_layer):
        if old_layer in self.layers:
            self.layers.insert(self.layers.index(old_layer), new_layer)
            self.layers.remove(old_layer)
            new_layer.__set_game__(self.game)
            old_layer.__set_game__(None)

    def event(self, event: pygame.event.Event):
        for layer in self.layers:
            layer.event(event)

    def paint(self, surface: Surface):
        for layer in self.layers:
            layer.surface.fill((0, 0, 0, 0))
            layer.paint(layer.surface)
            surface.blit(layer.surface, (0, 0))
