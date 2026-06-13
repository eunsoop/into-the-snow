import pygame

from entity.base import Entity

class CollectibleItem(Entity):

    def __init__(self, x: float, y: float, item_type: str):
        """
        Initialize the CollectibleItem.
        :param x: World X coordinate
        :param y: World Y coordinate
        :param item_type: String specifying item type (e.g., 'frozen_scrap', 'coal', etc.)
        """
        super().__init__(x, y)
        self.item_type = item_type
        self.rect = pygame.Rect(0, 0, 20, 20)
        self.rect.center = (int(self.x), int(self.y))

    def paint(self, surface: pygame.Surface):
        """
        Draw the collectible item rectangle with colors corresponding to its type.
        :param surface: Target drawing Surface
        """

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

class StolenPart(Entity):

    def __init__(self, x: float, y: float, part_type: str):
        """
        Initialize the StolenPart.
        :param x: World X coordinate
        :param y: World Y coordinate
        :param part_type: Part type identification string ('igniter', etc.)
        """
        super().__init__(x, y)
        self.part_type = part_type
        self.rect = pygame.Rect(0, 0, 24, 24)
        self.rect.center = (int(self.x), int(self.y))

    def paint(self, surface: pygame.Surface):
        """
        Draw the quest item on the floor.
        :param surface: Target drawing Surface
        """
        color = (255, 165, 0) if self.part_type == "igniter" else (0, 255, 255)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)

