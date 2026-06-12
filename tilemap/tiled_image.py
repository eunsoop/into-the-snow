import pygame
from pygame import Surface


class TiledImage:
    def __init__(self, tiles: Surface, tile_size: int):
        self.tiles = tiles.convert_alpha()
        self.tile_size = tile_size
        self.max_idx = tuple(map(lambda i: i / tile_size, self.tiles.get_size()))
        self._scaled_tiles = {}

    def get_tile_area(self, idx: int) -> tuple[int, int, int, int]:
        return (
            int((idx % self.max_idx[0]) * self.tile_size),
            int((idx // self.max_idx[0]) * self.tile_size),
            self.tile_size,
            self.tile_size,
        )

    def get_scaled_tile(self, tile_type: int, scale: float) -> Surface:
        key = (tile_type, scale)
        if key not in self._scaled_tiles:
            area = self.get_tile_area(tile_type)
            sub = self.tiles.subsurface(area)
            if scale == 1.0:
                self._scaled_tiles[key] = sub
            else:
                self._scaled_tiles[key] = pygame.transform.scale(
                    sub, (int(self.tile_size * scale), int(self.tile_size * scale))
                )
        return self._scaled_tiles[key]

    def draw(self, surface: Surface, coordinate: tuple[float, float], tile_type: int, scale: float):
        scaled_tile = self.get_scaled_tile(tile_type, scale)
        surface.blit(scaled_tile, coordinate)
