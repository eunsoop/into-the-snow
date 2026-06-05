import pygame
from pygame.locals import *

from entity import Entity


class Player(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.width = 32
        self.height = 32
        self.speed = 150
        self.temperature = 100.0
        self.wood = 0
        self.scrap = 0
        self.has_stun_gun = False
        self.has_hack_tool = False
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (int(self.x), int(self.y))

    def update(self):
        if self.layer and self.layer.get_game():
            dt = self.layer.get_game().get_dt()
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[K_w] or keys[K_UP]: dy -= self.speed * dt
            if keys[K_s] or keys[K_DOWN]: dy += self.speed * dt
            if keys[K_a] or keys[K_LEFT]: dx -= self.speed * dt
            if keys[K_d] or keys[K_RIGHT]: dx += self.speed * dt

            self.x += dx
            self.y += dy
            self.rect.center = (int(self.x), int(self.y))

            self.temperature -= 1.0 * dt
            if self.temperature <= 0:
                pass

    def paint(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (0, 255, 0), self.rect)