import math

import pygame
from pygame.locals import *

from entity.base import Entity


class Player(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.facing = (1.0, 0.0)
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

    def event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_h:
                if self.get_item_count("medkit") > 0 and self.health < 100.0:
                    self.remove_item("medkit", 1)
                    self.health = min(100.0, self.health + 40.0)
            elif event.key == K_t:
                if self.get_item_count("thermopack") > 0 and self.temperature < 100.0:
                    self.remove_item("thermopack", 1)
                    self.temperature = min(100.0, self.temperature + 50.0)

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

            if hasattr(self.layer, "is_platformer") and self.layer.is_platformer:
                self.temperature -= .5 * dt
                if self.temperature <= 0 or self.health <= 0:
                    self.temperature = max(0.0, self.temperature)
                    self.health = max(0.0, self.health)
                    self.layer.get_game().set_scene("gameover")
                return

            keys = pygame.key.get_pressed()
            dx = dy = 0
            if not (hasattr(self.layer, "state") and self.layer.state in ("CRAFTING", "ENGINE_UI")):
                if keys[K_w]:
                    dy -= self.speed * dt
                if keys[K_s]:
                    dy += self.speed * dt
                if keys[K_a]:
                    dx -= self.speed * dt
                if keys[K_d]:
                    dx += self.speed * dt
                if dx != 0 or dy != 0:
                    dist = math.hypot(dx, dy)
                    self.facing = (dx / dist, dy / dist)

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

            is_warming = False
            if hasattr(self.layer, "furnace") and self.layer.furnace:
                if self.layer.furnace.fuel > 0 and self.rect.inflate(80, 80).colliderect(self.layer.furnace.rect):
                    is_warming = True

            if is_warming:
                self.temperature = min(100.0, self.temperature + 12.0 * dt)
            else:
                self.temperature -= .5 * dt

            if self.temperature <= 0 or self.health <= 0:
                self.temperature = max(0.0, self.temperature)
                self.health = max(0.0, self.health)
                self.layer.get_game().set_scene("gameover")

    def paint(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (10, 180, 50), self.rect)
        pygame.draw.rect(surface, (100, 255, 120), self.rect, 2)
