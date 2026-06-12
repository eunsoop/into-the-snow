import pygame
from entity import Entity


class CollectibleItem(Entity):
    def __init__(self, x: float, y: float, item_type: str):
        super().__init__(x, y)
        self.item_type = item_type
        self.rect = pygame.Rect(0, 0, 20, 20)
        self.rect.center = (int(self.x), int(self.y))

    def paint(self, surface: pygame.Surface):
        if self.item_type == "frozen_scrap":
            color = (150, 150, 150)
            border_color = (220, 220, 220)
        elif self.item_type == "coal":
            color = (30, 30, 30)
            border_color = (80, 80, 80)
        else:
            color = (180, 120, 50)
            border_color = (240, 190, 100)

        pygame.draw.rect(surface, color, self.rect, border_radius=4)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=4)
