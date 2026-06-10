import pygame

from entity import Entity
from entity.projectile import Bullet


class Boss(Entity):
    def __init__(self, x: float, y: float, min_y: float, max_y: float):
        super().__init__(x, y)
        self.min_y = min_y
        self.max_y = max_y
        self.speed = 120
        self.direction = 1
        self.width = 64
        self.height = 64
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (int(self.x), int(self.y))
        self.hp = 100
        self.shoot_timer = 0.0

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
            self.rect.center = (int(self.x), int(self.y))

            self.shoot_timer += dt
            if self.shoot_timer >= 1.5:
                self.shoot_timer = 0.0
                b = Bullet(self.x - 40, self.y, -1.0, 0.0, is_enemy=True)
                b.speed = 220
                self.layer.add_entity(b)

    def paint(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (180, 0, 150), self.rect)
        pygame.draw.rect(surface, (255, 215, 0), self.rect, 3)


class Guard(Entity):
    def __init__(self, x: float, y: float, min_x: float, max_x: float):
        super().__init__(x, y)
        self.min_x = min_x
        self.max_x = max_x
        self.speed = 100
        self.direction = 1
        self.width = 32
        self.height = 32
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (int(self.x), int(self.y))
        self.is_stunned = False
        self.stun_timer = 0.0
        
        self.los_rect = pygame.Rect(0, 0, 150, 48)
        self.update_los()

    def update_los(self):
        if self.direction == 1:
            self.los_rect.x = self.rect.right
            self.los_rect.y = self.rect.y - 8
        else:
            self.los_rect.x = self.rect.left - 150
            self.los_rect.y = self.rect.y - 8

    def update(self):
        if self.layer and self.layer.get_game():
            dt = self.layer.get_game().get_dt()
            
            if self.is_stunned:
                self.stun_timer += dt
                if self.stun_timer >= 5.0:
                    self.is_stunned = False
                    self.stun_timer = 0.0
            else:
                self.x += self.speed * self.direction * dt
                if self.x > self.max_x:
                    self.x = self.max_x
                    self.direction = -1
                elif self.x < self.min_x:
                    self.x = self.min_x
                    self.direction = 1
                self.rect.center = (int(self.x), int(self.y))
                self.update_los()

    def paint(self, surface: pygame.Surface):
        if self.is_stunned:
            pygame.draw.rect(surface, (80, 80, 220), self.rect)
            pygame.draw.rect(surface, (150, 150, 255), self.rect, 2)
        else:
            pygame.draw.rect(surface, (180, 10, 10), self.rect)
            pygame.draw.rect(surface, (255, 100, 100), self.rect, 2)
            
            view_x = self.rect.x - (int(self.x) - self.width // 2)
            view_y = self.rect.y - (int(self.y) - self.height // 2)
            screen_los = self.los_rect.move(view_x, view_y)
            
            pygame.draw.rect(surface, (255, 50, 50), screen_los, 1)