from typing import Callable

from pygame import Surface

from scene import Layer


class TiledImage:
    def __init__(self, tiles: Surface, tile_size: int):
        self.tiles = tiles
        self.tile_size = tile_size
        self.max_idx = tuple(map(lambda i: i/tile_size, self.tiles.get_size()))

    def get_tile_area(self, idx: int) -> tuple[int, int, int, int]:
        return idx // self.max_idx[0] * self.tile_size, (idx % self.max_idx[0]) * self.tile_size, self.tile_size, self.tile_size

    def draw(self, surface: Surface, coordinate: tuple[int, int], tile_type: int, scale: float):
        surface.blit(self.tiles, (*map(lambda i: scale*i, coordinate), self.tile_size*scale, self.tile_size*scale), self.get_tile_area(tile_type))


class Viewpoint:
    __slots__ = ['x', 'y', 'z']
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class TilemapLayer(Layer):
    def __init__(self, tile: TiledImage, map_data: dict[int, list[tuple[int, Callable[[], bool]]]], viewpoint: Viewpoint = Viewpoint(0, 0, 40)):
        super().__init__()
        self.tile = tile
        self.map_data = map_data
        self.viewpoint = viewpoint

    def set_viewpoint(self, viewpoint: Viewpoint):
        self.viewpoint = viewpoint

    def event(self, event): pass

    def check_collision(self, other): pass # TODO: impl collision check

    def paint(self, surface: Surface):
        for y, tile in self.map_data:
            for x, tile_type in enumerate(tile):
                self.tile.draw(surface, (x, y), tile_type, 1)
