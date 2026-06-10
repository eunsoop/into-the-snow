import pygame

from entity import Entity


class Bullet(Entity):
    def __init__(self, x: float, y: float, dx: float, dy: float, is_enemy: bool = False):
        super().__init__(x, y)
        self.dx = dx
        self.dy = dy
        self.is_enemy = is_enemy
        self.speed = 300
        self.rect = pygame.Rect(0, 0, 8, 8)
        self.rect.center = (int(self.x), int(self.y))

    def update(self):
        if self.layer and self.layer.get_game():
            dt = self.layer.get_game().get_dt()
            self.x += self.dx * self.speed * dt
            self.y += self.dy * self.speed * dt
            self.rect.center = (int(self.x), int(self.y))

            if hasattr(self.layer, 'tilemap') and self.layer.tilemap:
                px = self.x - self.rect.width // 2
                py = self.y - self.rect.height // 2
                if self.layer.tilemap.check_collision(px, py, self.rect.width, self.rect.height):
                    self.layer.remove_entity(self)
                    
            if self.x < -100 or self.x > 3200 or self.y < -100 or self.y > 800:
                if self in self.layer.entities:
                    self.layer.remove_entity(self)

    def paint(self, surface: pygame.Surface):
        color = (255, 100, 0) if self.is_enemy else (255, 255, 0)
        pygame.draw.rect(surface, color, self.rect)
