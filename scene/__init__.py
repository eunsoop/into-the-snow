from abc import abstractmethod, ABC
from typing import final

import pygame
from pygame import Surface, surface

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
        self.surface = None

    @final
    def __set_game__(self, game):
        self.game = game
        self.surface = Surface(game.get_surface().get_size(), pygame.SRCALPHA) if game is not None else None
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
        self.effectors = []

    def __set_game__(self, game):
        super().__set_game__(game)
        for layer in self.layers:
            layer.__set_game__(game)

    def add_layer(self, layer: Layer):
        layer.__set_game__(self.game)
        self.layers.append(layer)

    def add_layers(self, layers: list[Layer]):
        for layer in layers:
            layer.__set_game__(self.game)
            self.add_layer(layer)

    def add_effector(self): pass

    def remove_layer(self, layer: Layer):
        if layer in self.layers:
            self.layers.remove(layer)
            layer.__set_game__(None)

    def replace_layer(self, old_layer: Layer, new_layer: Layer):
        if old_layer in self.layers:
            self.layers.insert(self.layers.index(old_layer), new_layer)
            self.layers.remove(old_layer)
            new_layer.__set_game__(self.game)
            old_layer.__set_game__(None)

    def event(self, event):
        for layer in self.layers: layer.event(event)

    def paint(self, surface: Surface):
        for layer in self.layers:
            layer.surface.fill((0, 0, 0, 0))
            layer.paint(layer.surface)
            surface.blit(layer.surface, (0, 0))


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

        self.backgrounds = list(map(scale_image, backgrounds))
        self.tick_time = 0

    def event(self, event): pass

    def tick(self):
        self.tick_time += 1

    def paint(self, surface: Surface):
        for bg in self.backgrounds:
            img, weight = bg
            surface.blit(img, (-(self.tick_time*weight%(img.get_width())), 0))
            surface.blit(img, (img.get_width()-(self.tick_time*weight%(img.get_width())), 0))


class RepeatingImageLayer(Layer):
    def __init__(self, img_data: tuple[str, float], axis: int, offset_x: int = 0, offset_y: int = 0, speed: float = 1):
        super().__init__()
        def scale_image(path, scale):
            img = pygame.image.load(path)
            return pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))

        self.img = scale_image(*img_data)
        self.axis = axis
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.tick_time = 0
        self.speed = speed

    def event(self, event): pass

    def tick(self):
        self.tick_time += 1

    def paint(self, surface: Surface):
        off = self.offset_x if self.axis == 0 else self.offset_y
        target = surface.get_width() if self.axis == 0 else surface.get_height()
        while off < target*self.speed:
            surface.blit(self.img, (off-((self.tick_time*self.speed)%(target*self.speed)), self.offset_y) if self.axis == 0 else (self.offset_x, off-((self.tick_time*self.speed)%(target*self.speed))))
            off += self.img.get_width() if self.axis == 0 else self.img.get_height()


class TrainLayer(Layer):
    def __init__(self, imgs: list[str], scale: float = 1, offset_x: int = 0, offset_y: int = 0):
        super().__init__()
        def scale_image(path):
            img = pygame.image.load(path)
            return pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        self.imgs = list(map(scale_image, imgs))
        self.max_height = max(img.get_height() for img in self.imgs)
        self.offset_x = offset_x
        self.offset_y = offset_y

    def event(self, event): pass

    def paint(self, surface: Surface):
        off = self.offset_x
        for img in self.imgs:
            surface.blit(img, (off, self.offset_y+self.max_height-img.get_height()))
            off += img.get_width()
