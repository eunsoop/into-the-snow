from abc import abstractmethod, ABC
from typing import final

import pygame
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

    def reset(self):
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

    def reset(self):
        for layer in self.layers:
            if hasattr(layer, "reset"):
                layer.reset()

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
        dt = self.game.get_dt() if self.game else 0.0
        for layer in self.layers:
            layer.surface.fill((0, 0, 0, 0))
            layer.paint(layer.surface)

            offset_x, offset_y = 0.0, 0.0
            active_effectors = []
            for eff in layer.effectors:
                eff.update(dt)
                if not eff.is_finished():
                    ox, oy = eff.apply_offset()
                    offset_x += ox
                    offset_y += oy
                    eff.apply_post(layer.surface)
                    active_effectors.append(eff)
            layer.effectors = active_effectors

            surface.blit(layer.surface, (int(offset_x), int(offset_y)))
