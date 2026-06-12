import random

import pygame

from entity.base import Entity
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


class DetachmentBoss(Boss):
    LEFT_FLOOR_Y = 344.0
    RIGHT_FLOOR_Y = 344.0
    COUPLER_Y = 284.0
    COUPLER_LEFT = 380.0
    COUPLER_RIGHT = 620.0
    LEFT_MAX_X = 300.0
    RIGHT_MIN_X = 700.0

    def __init__(self, x, y):
        super().__init__(x, y, 100, 100)
        self.speed = 130
        self.vy = 0.0
        self.on_ground = False
        self.width = 48
        self.height = 48
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (int(self.x), int(self.y))
        self.hp = 100
        self.shoot_timer = 0.0
        self.jump_cooldown = 0.0
        self.knockback_timer = 0.0
        self.knockback_vx = 0.0
        self.hit_flash = 0.0

    def _current_floor(self):
        coupling_severed = getattr(self.layer, 'coupling_severed', False)
        if self.x <= self.LEFT_MAX_X + 100:
            return self.LEFT_FLOOR_Y
        elif not coupling_severed and self.COUPLER_LEFT - 10 <= self.x <= self.COUPLER_RIGHT + 10:
            return self.COUPLER_Y
        else:
            return self.RIGHT_FLOOR_Y

    def _apply_platform_collision(self):
        coupling_severed = getattr(self.layer, 'coupling_severed', False)
        landed = False
        right_min = self.RIGHT_MIN_X + getattr(self.layer, 'separation_offset', 0.0)
        if self.x >= right_min and self.y >= self.RIGHT_FLOOR_Y and self.vy >= 0:
            self.y = self.RIGHT_FLOOR_Y
            self.vy = 0.0
            landed = True
        if not coupling_severed:
            if self.COUPLER_LEFT - 10 <= self.x <= self.COUPLER_RIGHT + 10 and self.y >= self.COUPLER_Y and self.vy >= 0:
                self.y = self.COUPLER_Y
                self.vy = 0.0
                landed = True
        if self.x <= self.LEFT_MAX_X + 100 and self.y >= self.LEFT_FLOOR_Y and self.vy >= 0:
            self.y = self.LEFT_FLOOR_Y
            self.vy = 0.0
            landed = True
        self.on_ground = landed

    def update(self):
        if not (self.layer and self.layer.get_game()):
            return
        dt = self.layer.get_game().get_dt()
        player = self.layer.player
        coupling_severed = getattr(self.layer, 'coupling_severed', False)
        self.vy += 1200.0 * dt
        self.y += self.vy * dt
        self._apply_platform_collision()
        self.knockback_timer -= dt
        self.hit_flash = max(0.0, self.hit_flash - dt)
        if self.knockback_timer > 0.0:
            self.x += self.knockback_vx * dt
            self.knockback_vx *= max(0.0, 1.0 - 8.0 * dt)
        else:
            if player:
                if player.x < self.x:
                    self.x -= self.speed * dt
                else:
                    self.x += self.speed * dt
        self.jump_cooldown -= dt
        if self.on_ground and self.jump_cooldown <= 0.0:
            should_jump = False
            if self.x > self.RIGHT_MIN_X - 20 and self.x < self.COUPLER_RIGHT + 40:
                should_jump = True
            elif self.COUPLER_LEFT - 40 <= self.x <= self.COUPLER_LEFT + 60:
                should_jump = True
            elif random.random() < 0.015:
                should_jump = True
            if should_jump:
                self.vy = -480.0
                self.on_ground = False
                self.jump_cooldown = 1.2
        self.x = max(80.0, self.x)
        separation_offset = getattr(self.layer, 'separation_offset', 0.0)
        self.x = min(920.0 + separation_offset, self.x)
        self.rect.center = (int(self.x), int(self.y + self.height // 2))
        if self.x <= self.LEFT_MAX_X and not coupling_severed:
            if self.on_ground:
                self.layer.get_game().set_scene("gameover")
                return
        self.shoot_timer += dt
        if self.shoot_timer >= 1.5:
            self.shoot_timer = 0.0
            if player:
                dir_x = -1.0 if player.x < self.x else 1.0
                b = Bullet(self.x - 24, self.y + self.height // 2, dir_x, 0.0, is_enemy=True)
                b.speed = 260
                self.layer.add_entity(b)

    def paint(self, surface: pygame.Surface):
        body_color = (255, 200, 200) if self.hit_flash > 0 else (50, 20, 20)
        pygame.draw.rect(surface, body_color, self.rect, border_radius=6)
        pygame.draw.rect(surface, (220, 60, 60), self.rect, width=2, border_radius=6)
        eye = (self.rect.centerx - 8, self.rect.centery - 6)
        pygame.draw.circle(surface, (255, 60, 60), eye, 9)
        pygame.draw.circle(surface, (255, 200, 200), eye, 4)
        pygame.draw.line(surface, (180, 180, 180),
                         (self.rect.left - 10, self.rect.centery),
                         (self.rect.left, self.rect.centery), 4)
        pygame.draw.line(surface, (180, 180, 180),
                         (self.rect.right, self.rect.centery),
                         (self.rect.right + 10, self.rect.centery), 4)
        bar_w = self.width
        bar_x = self.rect.x
        bar_y = self.rect.y - 10
        pygame.draw.rect(surface, (80, 0, 0), pygame.Rect(bar_x, bar_y, bar_w, 6))
        filled = int(bar_w * max(0, self.hp) / 100)
        pygame.draw.rect(surface, (220, 50, 50), pygame.Rect(bar_x, bar_y, filled, 6))