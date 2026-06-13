import pygame
from pygame import Surface

from core import Layer

class WeightedBackgroundLayer(Layer):

    def __init__(self, backgrounds: list[tuple[str, float]], offset_y: int = 0, scale_factor: float = 1):
        """
        Initialize the WeightedBackgroundLayer.
        :param backgrounds: List of tuples (image_path, speed_weight)
        :param offset_y: Vertical offset in pixels
        :param scale_factor: Resize multiplier
        """
        super().__init__()

        def scale_image(bg):
            """
            Scale a background layer image and pair it with its scrolling speed weight.
            :param bg: Tuple (image_path, weight)
            :return: Tuple (scaled_image_surface, weight)
            """
            path, weight = bg
            img = pygame.image.load(path)

            scale = max(1000 / img.get_width(), 700 / img.get_height())*scale_factor
            return pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale))), weight

        self.backgrounds = list(map(scale_image, backgrounds))
        self.tick_time = 0
        self.offset_y = offset_y*scale_factor

    def event(self, event):
        pass

    def tick(self):
        self.tick_time += 1

    def paint(self, surface: Surface):
        for bg in self.backgrounds:
            img, weight = bg

            surface.blit(img, (-(self.tick_time * weight % (img.get_width())), self.offset_y))
            surface.blit(img, (img.get_width() - (self.tick_time * weight % (img.get_width())), self.offset_y))

class RepeatingImageLayer(Layer):

    def __init__(self, img_data: tuple[str, float], axis: int, offset_x: int = 0, offset_y: int = 0, speed: float = 1):
        """
        Initialize the RepeatingImageLayer.
        :param img_data: Tuple (image_path, scale_factor)
        :param axis: Axis to repeat along (0 for X axis, 1 for Y axis)
        :param offset_x: Horizontal starting offset
        :param offset_y: Vertical starting offset
        :param speed: Scrolling speed factor
        """
        super().__init__()

        def scale_image(path, scale):
            """
            Load and scale a single image to the specified scale factor.
            :param path: Filesystem path to image asset
            :param scale: Size multiplier float
            :return: Scaled pygame.Surface image
            """
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
        """
        Draw repeated tile images along the specified axis.
        :param surface: Target drawing Surface
        """
        off = self.offset_x if self.axis == 0 else self.offset_y
        target = surface.get_width() if self.axis == 0 else surface.get_height()

        while off < target * self.speed:
            if self.axis == 0:
                pos = (off - ((self.tick_time * self.speed) % (target * self.speed)), self.offset_y)
            else:
                pos = (self.offset_x, off - ((self.tick_time * self.speed) % (target * self.speed)))
            surface.blit(self.img, pos)
            off += self.img.get_width() if self.axis == 0 else self.img.get_height()

class TrainLayer(Layer):

    def __init__(self, imgs: list[str], scale: float = 1, offset_x: int = 0, offset_y: int = 0):
        """
        Initialize the TrainLayer.
        :param imgs: List of image paths representing train cars
        :param scale: Size scale multiplier
        :param offset_x: Starting horizontal coordinate offset
        :param offset_y: Starting vertical coordinate offset
        """
        super().__init__()

        def scale_image(path):
            """
            Load and scale a train car image.
            :param path: Filesystem path to train car image asset
            :return: Scaled pygame.Surface image
            """
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

            surface.blit(img, (off, self.offset_y + self.max_height - img.get_height()))
            off += img.get_width()

