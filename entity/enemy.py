import pygame

from entity import Entity


class Boss(Entity):
    def __init__(self, x: float, y: float, min_y: float, max_y: float):
        super().__init__(x, y)
        self.min_y = min_y
        self.max_y = max_y
        self.speed = 150
        self.direction = 1
        self.width = 64
        self.height = 64
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.hp = 100

    def update(self):
        if self.layer and self.layer.get_game():
            dt = self.layer.get_game().get_dt()
            self.y += self.speed * self.direction * dt
            if self.y > self.max_y:
                self.y = self.max_y
                self.direction = -1
            elif self.y < self.min_y:
                self.y = self.min_y
                self.direction = 1
            self.rect.topleft = (self.x, self.y)

    def paint(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (200, 0, 200), self.rect)


class Guard(Entity):
    def __init__(self, x: float, y: float, min_x: float, max_x: float):
        super().__init__(x, y)
        self.min_x = min_x
        self.max_x = max_x
        self.speed = 100
        self.direction = 1
        self.width = 32
        self.height = 32
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.is_stunned = False

    def update(self):
        if not self.is_stunned and self.layer and self.layer.get_game():
            dt = self.layer.get_game().get_dt()
            self.x += self.speed * self.direction * dt
            if self.x > self.max_x:
                self.x = self.max_x
                self.direction = -1
            elif self.x < self.min_x:
                self.x = self.min_x
                self.direction = 1
            self.rect.topleft = (int(self.x), int(self.y))

    def paint(self, surface: pygame.Surface):
        color = (100, 100, 255) if self.is_stunned else (255, 0, 0)
        pygame.draw.rect(surface, color, self.rect)


class Bullet(Entity):
    def __init__(self, x: float, y: float, dx: float, dy: float):
        super().__init__(x, y)
        self.dx = dx
        self.dy = dy
        self.speed = 300
        self.rect = pygame.Rect(self.x, self.y, 8, 8)

    def update(self):
        if self.layer and self.layer.get_game():
            dt = self.layer.get_game().get_dt()
            self.x += self.dx * self.speed * dt
            self.y += self.dy * self.speed * dt
            self.rect.topleft = (int(self.x), int(self.y))

    def paint(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (255, 255, 0), self.rect)