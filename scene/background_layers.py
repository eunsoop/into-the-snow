import pygame
from pygame import Surface

from core import Layer


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

    def event(self, event):
        pass

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

    def event(self, event):
        pass

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

    def event(self, event):
        pass

    def paint(self, surface: Surface):
        off = self.offset_x
        for img in self.imgs:
            surface.blit(img, (off, self.offset_y+self.max_height-img.get_height()))
            off += img.get_width()
