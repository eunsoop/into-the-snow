import math
import time

import pygame

from entity.base import Entity


class Furnace(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.is_solid = True
        self.fuel = 50.0
        self.rect = pygame.Rect(0, 0, 64, 64)
        self.rect.center = (int(self.x), int(self.y))

    def paint(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (45, 45, 50), self.rect, border_radius=8)
        pygame.draw.rect(surface, (75, 75, 80), self.rect, width=3, border_radius=8)
        door_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 18, 44, 30)
        pygame.draw.rect(surface, (20, 20, 20), door_rect, border_radius=4)
        if self.fuel > 0:
            flicker = 15 * math.sin(time.time() * 15) + (pygame.time.get_ticks() % 12)
            glow_radius = max(8, min(14, int(11 + flicker * 0.15)))
            pygame.draw.circle(surface, (255, max(80, int(110 + flicker)), 10), door_rect.center, glow_radius)
            pygame.draw.circle(surface, (255, 240, 150), door_rect.center, int(glow_radius * 0.55))


class CraftingTable(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.is_solid = True
        self.rect = pygame.Rect(0, 0, 64, 64)
        self.rect.center = (int(self.x), int(self.y))

    def paint(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (70, 52, 40), self.rect, border_radius=6)
        pygame.draw.rect(surface, (100, 80, 65), self.rect, width=3, border_radius=6)
        bp = pygame.Rect(self.rect.x + 12, self.rect.y + 12, 40, 24)
        pygame.draw.rect(surface, (35, 75, 140), bp, border_radius=2)
        pygame.draw.rect(surface, (170, 210, 255), bp, width=1, border_radius=2)
        pygame.draw.line(surface, (255, 255, 255), (bp.x + 6, bp.y + 6), (bp.right - 6, bp.y + 6), 1)
        pygame.draw.line(surface, (255, 255, 255), (bp.x + 6, bp.y + 12), (bp.right - 14, bp.y + 12), 1)
        pygame.draw.line(surface, (255, 255, 255), (bp.x + 6, bp.y + 18), (bp.right - 8, bp.y + 18), 1)


class BrokenEngineCore(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.is_solid = True
        self.rect = pygame.Rect(0, 0, 96, 128)
        self.rect.center = (int(self.x), int(self.y))
        self.img = pygame.image.load("assets/images/objects/engine.png")

    def paint(self, surface: pygame.Surface):
        surface.blit(self.img, self.rect)