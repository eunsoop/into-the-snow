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
        self.health = 100.0
        self.inventory = {}
        self.transition_x = None
        self.spotted_shake = False
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (int(self.x), int(self.y))

    def add_item(self, item: str, amount: int = 1):
        self.inventory[item] = self.inventory.get(item, 0) + amount

    def remove_item(self, item: str, amount: int = 1) -> bool:
        if self.get_item_count(item) >= amount:
            self.inventory[item] -= amount
            return True
        return False

    def get_item_count(self, item: str) -> int:
        return self.inventory.get(item, 0)

    def has_item(self, item: str) -> bool:
        return self.get_item_count(item) > 0

    def pop_transition_x(self) -> float | None:
        val = self.transition_x
        self.transition_x = None
        return val

    def pop_spotted_shake(self) -> bool:
        val = self.spotted_shake
        self.spotted_shake = False
        return val

    def update(self):
        if self.layer and self.layer.get_game():
            dt = self.layer.get_game().get_dt()
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[K_w] or keys[K_UP]:
                dy -= self.speed * dt
            if keys[K_s] or keys[K_DOWN]:
                dy += self.speed * dt
            if keys[K_a] or keys[K_LEFT]:
                dx -= self.speed * dt
            if keys[K_d] or keys[K_RIGHT]:
                dx += self.speed * dt

            new_x = self.x + dx
            px = new_x - self.width // 2
            py = self.y - self.height // 2
            
            if hasattr(self.layer, 'tilemap') and self.layer.tilemap:
                if not self.layer.tilemap.check_collision(px, py, self.width, self.height):
                    self.x = new_x
            else:
                self.x = new_x

            new_y = self.y + dy
            px = self.x - self.width // 2
            py = new_y - self.height // 2
            
            if hasattr(self.layer, 'tilemap') and self.layer.tilemap:
                if not self.layer.tilemap.check_collision(px, py, self.width, self.height):
                    self.y = new_y
            else:
                self.y = new_y

            self.rect.center = (int(self.x), int(self.y))

            self.temperature -= 3.0 * dt
            if self.temperature <= 0 or self.health <= 0:
                self.temperature = max(0.0, self.temperature)
                self.health = max(0.0, self.health)
                self.layer.get_game().set_scene("gameover")

    def paint(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (10, 180, 50), self.rect)
        pygame.draw.rect(surface, (100, 255, 120), self.rect, 2)