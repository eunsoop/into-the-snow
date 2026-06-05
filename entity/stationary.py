import pygame

from entity import Entity


class Furnace(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.rect = pygame.Rect(0, 0, 64, 64)
        self.rect.center = (int(self.x), int(self.y))

    def paint(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (255, 100, 0), self.rect)


class CraftingTable(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.rect = pygame.Rect(0, 0, 64, 64)
        self.rect.center = (int(self.x), int(self.y))

    def paint(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (100, 100, 100), self.rect)


class Hatch(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.rect = pygame.Rect(0, 0, 64, 64)
        self.rect.center = (int(self.x), int(self.y))

    def paint(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (50, 50, 50), self.rect)