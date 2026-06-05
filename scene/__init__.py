from abc import abstractmethod, ABC
from typing import final

import pygame
from pygame import Surface

from entity import Entity


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
    def __init__(self, layers: list[Layer] = None):
        super().__init__()
        self.layers = layers if layers is not None else []

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


class GameLayer(Layer):
    def __init__(self):
        super().__init__()
        self.entities = []

    def add_entity(self, entity: Entity):
        self.entities.append(entity)
        entity.layer = self

    def remove_entity(self, entity: Entity):
        if entity in self.entities:
            self.entities.remove(entity)
            entity.layer = None

    def event(self, event):
        for e in self.entities:
            e.event(event)

    def update(self): pass

    def paint(self, surface: Surface):
        self.update()
        for e in self.entities:
            e.update()
        for e in sorted(self.entities, key=lambda e: e.z_index):
            e.paint(surface)


class WeightedBackgroundLayer(Layer):
    def __init__(self, backgrounds: list[tuple[str, float]]):
        super().__init__()
        def scale_image(bg):
            path, weight = bg
            img = pygame.image.load(path)
            scale = max(1000 / img.get_width(), 700 / img.get_height())
            return pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale))), weight

        self.backgrounds = map(scale_image, backgrounds)
        self.tick = 0

    def event(self, event): pass

    def tick(self):
        self.tick += 1

    def paint(self, surface: Surface):
        for bg in self.backgrounds:
            img, weight = bg
            surface.blit(img, (self.tick*weight, 0))

