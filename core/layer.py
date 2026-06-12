from abc import abstractmethod, ABC
from typing import final

import pygame
from pygame import Surface

from core.effector import Effector


class Layer(ABC):
    def __init__(self):
        self.game = None
        self.surface = None
        self.effectors = []

    def add_effector(self, effector: Effector):
        self.effectors.append(effector)

    @final
    def __set_game__(self, game):
        self.game = game
        self.surface = Surface(game.get_surface().get_size(), pygame.SRCALPHA) if game is not None else None

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


class GameLayer(Layer):
    def __init__(self):
        super().__init__()
        self.entities = []

    def add_entity(self, entity):
        self.entities.append(entity)
        entity.layer = self

    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)
            entity.layer = None

    def event(self, event: pygame.event.Event):
        for e in self.entities:
            e.event(event)

    def update(self):
        pass

    def paint(self, surface: Surface):
        self.update()
        for e in self.entities:
            e.update()

        if hasattr(self, 'tilemap') and self.tilemap:
            player = getattr(self, 'player', None)
            if player:
                width, height = surface.get_width(), surface.get_height()
                view_x = width / 2 - player.x
                view_y = height / 2 - player.y

                ts = self.tilemap.tile.tile_size * self.tilemap.viewpoint.z
                map_width = len(self.tilemap.map_data[next(iter(self.tilemap.map_data))]) * ts if self.tilemap.map_data else 0
                map_height = len(self.tilemap.map_data) * ts

                min_x = width - map_width
                min_y = height - map_height

                if min_x > 0:
                    view_x = min_x / 2
                else:
                    view_x = max(min_x, min(0, view_x))

                if min_y > 0:
                    view_y = min_y / 2
                else:
                    view_y = max(min_y, min(0, view_y))

                self.tilemap.viewpoint.x = view_x
                self.tilemap.viewpoint.y = view_y

            self.tilemap.paint(surface)

        viewpoint = getattr(self.tilemap, 'viewpoint', None) if hasattr(self, 'tilemap') and self.tilemap else None
        for e in sorted(self.entities, key=lambda e: e.z_index):
            if viewpoint:
                orig_center = e.rect.center
                e.rect.x += viewpoint.x
                e.rect.y += viewpoint.y
                e.paint(surface)
                e.rect.center = orig_center
            else:
                e.paint(surface)
