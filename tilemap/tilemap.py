import pygame
from pygame import Surface

from tilemap.tiled_image import TiledImage
from tilemap.viewpoint import Viewpoint


class Tilemap:
    def __init__(self, tile: TiledImage, map_data: dict, viewpoint: Viewpoint = Viewpoint(0, 0, 40)):
        self.tile = tile
        self.map_data = map_data
        self.viewpoint = viewpoint
        self.stationaries = []

    def set_viewpoint(self, viewpoint: Viewpoint):
        self.viewpoint = viewpoint

    def add_stationary(self, obj):
        self.stationaries.append(obj)

    def check_collision(self, px: float, py: float, pw: float, ph: float) -> bool:
        world_x = px
        world_y = py
        ts = self.tile.tile_size * self.viewpoint.z
        start_y = int(world_y // ts)
        end_y = int((world_y + ph) // ts)
        start_x = int(world_x // ts)
        end_x = int((world_x + pw) // ts)
        for y in range(start_y, end_y + 1):
            if y in self.map_data:
                row = self.map_data[y]
                for x in range(start_x, end_x + 1):
                    if 0 <= x < len(row):
                        _, passable = row[x]
                        if not passable():
                            return True
        player_world_rect = pygame.Rect(world_x, world_y, pw, ph)
        for obj in self.stationaries:
            if getattr(obj, "is_solid", True):
                if player_world_rect.colliderect(obj.rect):
                    return True
        return False

    def paint(self, surface: Surface):
        ts = self.tile.tile_size * self.viewpoint.z
        for y, row in self.map_data.items():
            screen_y = y * ts + self.viewpoint.y
            if screen_y + ts < 0 or screen_y > surface.get_height():
                continue
            for x, (tile_type, _) in enumerate(row):
                screen_x = x * ts + self.viewpoint.x
                if screen_x + ts < 0 or screen_x > surface.get_width():
                    continue
                self.tile.draw(surface, (screen_x, screen_y), tile_type, self.viewpoint.z)
        for obj in self.stationaries:
            orig_center = obj.rect.center
            obj.rect.x += self.viewpoint.x
            obj.rect.y += self.viewpoint.y
            obj.paint(surface)
            obj.rect.center = orig_center
