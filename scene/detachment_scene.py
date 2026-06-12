import random
import math
import pygame
from pygame.locals import *

from core import LayeredScene, GameLayer, Fonts, ShakeEffector, FlashEffector, TrainShakeEffector
from entity.projectile import Bullet
from entity.enemy import Boss
from tilemap import TiledImage, Tilemap, Viewpoint


class DetachmentBoss(Boss):
    LEFT_FLOOR_Y  = 360.0 - 16.0
    RIGHT_FLOOR_Y = 360.0 - 16.0
    COUPLER_Y     = 300.0 - 16.0
    COUPLER_LEFT  = 380.0
    COUPLER_RIGHT = 620.0
    LEFT_MAX_X    = 300.0
    RIGHT_MIN_X   = 700.0

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
        """Return the expected floor y for the boss's current x position."""
        coupling_severed = getattr(self.layer, 'coupling_severed', False)
        if self.x <= self.LEFT_MAX_X + 100:
            return self.LEFT_FLOOR_Y
        elif not coupling_severed and self.COUPLER_LEFT - 10 <= self.x <= self.COUPLER_RIGHT + 10:
            return self.COUPLER_Y
        else:
            return self.RIGHT_FLOOR_Y

    def _apply_platform_collision(self):
        """Snap boss to whichever platform it is standing on."""
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


class DetachmentGameLayer(GameLayer):
    def __init__(self):
        super().__init__()
        self.is_platformer = True

        self.tilemap = self.setup_map(Viewpoint(0, 0, 5))
        self.player = None
        self.boss = None
        self.boss_spawned = False
        self.combat_active = False
        self.coupling_severed = False
        self.separation_offset = 0.0
        self.separation_timer = 2.5

        self.player_vx = 0.0
        self.player_vy = 0.0
        self.player_on_ground = False
        self.player_speed = 200.0
        self.fire_cooldown_timer = 0.15

        self.hud_message = ""
        self.hud_message_timer = 0.0

        self.snow_particles = [
            {
                "x": random.randint(0, 1000),
                "y": random.randint(100, 550),
                "length": random.randint(15, 30),
                "speed": random.randint(600, 1000)
            }
            for _ in range(30)
        ]

        self.add_effector(TrainShakeEffector(base_intensity=0.5, jolt_frequency=4.0, jolt_intensity=2.0, jolt_duration=0.4))

    def setup_map(self, viewpoint: Viewpoint) -> Tilemap:
        tiles_surf = pygame.image.load("assets/images/tilemap/tilemap.png").convert_alpha()
        tiled_image = TiledImage(tiles_surf, tile_size=8)

        map_data = {}
        for y in range(12):
            row = []
            for x in range(25):
                is_left_car_floor = (y == 9 and x < 8)
                is_right_car_floor = (y == 9 and x >= 18)
                is_left_wall = (x == 0 and y < 9)
                is_right_wall = (x == 24 and y < 9)
                is_ceiling = (y == 0)

                if is_left_car_floor or is_right_car_floor:
                    row.append((4, lambda: False))
                elif is_left_wall or is_right_wall or is_ceiling:
                    row.append((4, lambda: False))
                else:
                    row.append((2, lambda: True))
            map_data[y] = row

        return Tilemap(tiled_image, map_data, viewpoint)

    def on_enter(self):
        game = self.get_game()
        self.player = game.player
        self.add_entity(self.player)

        tx = self.player.pop_transition_x()
        if tx is not None:
            self.player.x = tx

        self.player.y = 360.0 - 16.0
        self.player.rect.center = (int(self.player.x), int(self.player.y))

        self.player_vx = 0.0
        self.player_vy = 0.0
        self.player_on_ground = True

        engine_room = self.game.scenes["ingame.engineroom"].logic_layer
        if engine_room.engine_repaired and not self.coupling_severed:
            self.combat_active = True
            self.add_effector(FlashEffector(duration=0.5, color=(255, 0, 0), max_alpha=100))
            if not self.boss_spawned:
                self.boss_spawned = True
                self.boss = DetachmentBoss(800, 360 - 16)
                self.add_entity(self.boss)

                if not self.player.has_item("ak47"):
                    self.player.add_item("ak47", 1)
                    self.hud_message = "EMERGENCY: AK-47 RIFLE ACQUIRED"
                    self.hud_message_timer = 3.0

    def reset(self):
        if self.player and self.player in self.entities:
            self.remove_entity(self.player)
        self.player = None
        self.combat_active = False
        self.boss_spawned = False
        self.coupling_severed = False
        self.separation_offset = 0.0
        self.separation_timer = 2.5
        self.hud_message = ""
        self.hud_message_timer = 0.0
        self.player_vx = 0.0
        self.player_vy = 0.0
        self.player_on_ground = False

        for e in self.entities[:]:
            if isinstance(e, (DetachmentBoss, Bullet)) or (self.boss and e == self.boss):
                self.remove_entity(e)
        self.boss = None

    def event(self, event):
        super().event(event)

    def update(self):
        super().update()
        dt = self.game.get_dt()

        for p in self.snow_particles:
            speed_mult = 1.8 if self.coupling_severed else (1.4 if self.combat_active else 1.0)
            p["x"] -= p["speed"] * speed_mult * dt
            if p["x"] < 0:
                p["x"] = 1000
                p["y"] = random.randint(100, 550)

        if self.hud_message_timer > 0.0:
            self.hud_message_timer -= dt
            if self.hud_message_timer <= 0.0:
                self.hud_message = ""

        self.player_vy += 1200.0 * dt

        keys = pygame.key.get_pressed()
        self.player_vx = 0.0
        if keys[K_a]:
            self.player_vx = -self.player_speed
        if keys[K_d]:
            self.player_vx = self.player_speed

        if keys[K_w] and self.player_on_ground:
            self.player_vy = -450.0
            self.player_on_ground = False

        mx, my = pygame.mouse.get_pos()
        vx, vy = 0, 110
        if mx < self.player.x + vx:
            self.player.facing = (-1.0, 0.0)
        else:
            self.player.facing = (1.0, 0.0)

        self.player.x += self.player_vx * dt

        if self.coupling_severed:
            self.separation_timer -= dt
            self.separation_offset += 250.0 * dt
            if self.separation_timer <= 0.0:
                self.remove_entity(self.player)
                self.game.set_scene("gamewin")
                return
            self.player.x = max(100.0, min(800.0, self.player.x))
        elif self.combat_active:
            self.player.x = max(100.0, min(900.0, self.player.x))
        else:
            if self.player.x < 15:
                self.player.transition_x = 2800
                self.remove_entity(self.player)
                self.game.set_scene("ingame.engineroom")
                return
            elif self.player.x > 985:
                self.player.transition_x = 100
                self.remove_entity(self.player)
                self.game.set_scene("ingame.tailworkshop")
                return

        self.player.rect.centerx = int(self.player.x)

        self.player.y += self.player_vy * dt

        self.player_on_ground = False

        if self.player.x <= 300.0 and self.player.y + 16.0 >= 360.0 and self.player_vy >= 0:
            self.player.y = 360.0 - 16.0
            self.player_vy = 0.0
            self.player_on_ground = True

        right_limit = 700.0 + self.separation_offset
        if self.player.x >= right_limit and self.player.y + 16.0 >= 360.0 and self.player_vy >= 0:
            self.player.y = 360.0 - 16.0
            self.player_vy = 0.0
            self.player_on_ground = True

        if not self.coupling_severed:
            if 380.0 <= self.player.x <= 620.0 and self.player.y + 16.0 >= 300.0 and self.player.y + 16.0 - self.player_vy * dt <= 308.0 and self.player_vy >= 0:
                self.player.y = 300.0 - 16.0
                self.player_vy = 0.0
                self.player_on_ground = True

        self.player.rect.centery = int(self.player.y)

        if self.player.y > 500.0:
            self.player.health = 0.0
            self.game.set_scene("gameover")
            return

        if not self.coupling_severed and self.player.has_item("ak47"):
            self.fire_cooldown_timer = max(0.0, self.fire_cooldown_timer - dt)
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0] and self.fire_cooldown_timer <= 0.0:
                self.fire_cooldown_timer = 0.12
                mx, my = pygame.mouse.get_pos()
                px_screen = self.player.x
                py_screen = self.player.y + 110.0
                dx = mx - px_screen
                dy = my - py_screen
                dist = math.hypot(dx, dy)
                if dist > 0:
                    dx /= dist
                    dy /= dist
                else:
                    dx, dy = self.player.facing[0], 0.0
                b = Bullet(self.player.x, self.player.y, dx, dy, is_enemy=False)
                b.speed = 600
                self.add_entity(b)
                self.add_effector(ShakeEffector(duration=0.06, intensity=1.2))

        bullets = [e for e in self.entities if isinstance(e, Bullet)]
        for b in bullets:
            if b.is_enemy:
                if b.rect.colliderect(self.player.rect) and not self.coupling_severed:
                    self.player.health = max(0.0, self.player.health - 15.0)
                    self.add_effector(ShakeEffector(duration=0.3, intensity=10.0))
                    self.add_effector(FlashEffector(duration=0.15, color=(255, 0, 0), max_alpha=128))
                    if b in self.entities:
                        self.remove_entity(b)
            else:
                if self.boss and self.boss in self.entities and b.rect.colliderect(self.boss.rect):
                    self.boss.hp -= 10
                    self.boss.knockback_timer = 0.6
                    self.boss.knockback_vx = 350.0
                    self.boss.hit_flash = 0.15
                    self.boss.vy = -200.0
                    if b in self.entities:
                        self.remove_entity(b)
                    self.add_effector(ShakeEffector(duration=0.15, intensity=4.0))
                    if self.boss.hp <= 0:
                        self.remove_entity(self.boss)
                        self.coupling_severed = True
                        self.add_effector(ShakeEffector(duration=2.5, intensity=12.0))
                        self.add_effector(FlashEffector(duration=0.5, color=(255, 255, 255), max_alpha=200))
                    break

    def paint_tilemap(self, surface: pygame.Surface):
        ts = self.tilemap.tile.tile_size * self.tilemap.viewpoint.z
        for y, row in self.tilemap.map_data.items():
            screen_y = y * ts + self.tilemap.viewpoint.y
            for x, (tile_type, _) in enumerate(row):
                x_offset = self.separation_offset if x >= 18 else 0.0
                screen_x = x * ts + self.tilemap.viewpoint.x + x_offset
                if screen_x + ts < 0 or screen_x > surface.get_width():
                    continue
                self.tilemap.tile.draw(surface, (screen_x, screen_y), tile_type, self.tilemap.viewpoint.z)

    def paint(self, surface: pygame.Surface):
        self.update()
        for e in self.entities:
            e.update()

        viewpoint = self.tilemap.viewpoint
        viewpoint.x = 0
        viewpoint.y = 110

        surface.fill((10, 12, 18))

        pygame.draw.polygon(surface, (18, 20, 28), [(0, 400), (250, 250), (500, 380), (750, 220), (1000, 400), (1000, 700), (0, 700)])
        pygame.draw.polygon(surface, (14, 16, 22), [(0, 480), (350, 300), (700, 450), (1000, 320), (1000, 700), (0, 700)])

        for p in self.snow_particles:
            pygame.draw.line(surface, (200, 200, 220), (p["x"], p["y"]), (p["x"] - p["length"], p["y"] + p["length"] // 4), 2)

        self.paint_tilemap(surface)

        for obj in sorted(self.entities, key=lambda e: e.z_index):
            if obj not in self.tilemap.stationaries:
                orig_center = obj.rect.center
                obj.rect.x += viewpoint.x
                obj.rect.y += viewpoint.y
                obj.paint(surface)
                obj.rect.center = orig_center

        vx, vy = viewpoint.x, viewpoint.y

        if not self.coupling_severed:
            pygame.draw.line(surface, (100, 100, 100), (300 + vx, 360 + vy), (380 + vx, 300 + vy), 6)
            pygame.draw.line(surface, (100, 100, 100), (620 + vx, 300 + vy), (700 + self.separation_offset + vx, 360 + vy), 6)
            pygame.draw.line(surface, (80, 80, 80), (380 + vx, 300 + vy), (620 + self.separation_offset + vx, 300 + vy), 12)
            pygame.draw.line(surface, (140, 140, 140), (380 + vx, 300 + vy), (620 + self.separation_offset + vx, 300 + vy), 4)
        else:
            pygame.draw.line(surface, (100, 100, 100), (300 + vx, 360 + vy), (380 + vx, 300 + vy), 6)
            pygame.draw.line(surface, (80, 80, 80), (380 + vx, 300 + vy), (480 + vx, 320 + vy), 12)
            pygame.draw.line(surface, (140, 140, 140), (380 + vx, 300 + vy), (480 + vx, 320 + vy), 4)
            pygame.draw.line(surface, (100, 100, 100), (620 + self.separation_offset + vx, 300 + vy), (700 + self.separation_offset + vx, 360 + vy), 6)
            pygame.draw.line(surface, (80, 80, 80), (520 + self.separation_offset + vx, 320 + vy), (620 + self.separation_offset + vx, 300 + vy), 12)
            pygame.draw.line(surface, (140, 140, 140), (520 + self.separation_offset + vx, 320 + vy), (620 + self.separation_offset + vx, 300 + vy), 4)

        if self.combat_active and not self.coupling_severed:
            pygame.draw.line(surface, (255, 50, 50), (80 + vx, 240 + vy), (80 + vx, 380 + vy), 4)
            pygame.draw.line(surface, (255, 120, 120), (80 + vx, 240 + vy), (80 + vx, 380 + vy), 2)
            pygame.draw.line(surface, (255, 50, 50), (920 + self.separation_offset + vx, 240 + vy), (920 + self.separation_offset + vx, 380 + vy), 4)
            pygame.draw.line(surface, (255, 120, 120), (920 + self.separation_offset + vx, 240 + vy), (920 + self.separation_offset + vx, 380 + vy), 2)

        if self.player and self.combat_active and not self.coupling_severed:
            mx, my = pygame.mouse.get_pos()
            px_s = int(self.player.x + vx)
            py_s = int(self.player.y + vy)
            aim_dx = mx - px_s
            aim_dy = my - py_s
            aim_dist = math.hypot(aim_dx, aim_dy)
            if aim_dist > 0:
                aim_dx /= aim_dist
                aim_dy /= aim_dist
            end_x = int(px_s + aim_dx * 60)
            end_y = int(py_s + aim_dy * 60)
            pygame.draw.line(surface, (255, 255, 100, 160), (px_s, py_s), (end_x, end_y), 2)
            pygame.draw.circle(surface, (255, 255, 0), (mx, my), 5, 2)

        font_prompt = Fonts.Jersey_10(24)
        if self.hud_message:
            msg_surf = font_prompt.render(self.hud_message, True, (255, 100, 100))
            surface.blit(msg_surf, (surface.get_width() // 2 - msg_surf.get_width() // 2, 200))

        font_lbl = Fonts.Jersey_10(20)
        lines = [
            f"HP: {int(self.player.health)}",
            f"Temp: {int(self.player.temperature)}"
        ]
        if self.combat_active:
            boss_hp_str = str(self.boss.hp) if (self.boss and self.boss in self.entities) else "DESTROYED"
            lines.append(f"Boss: {boss_hp_str}")

        y_offset = 20
        for line in lines:
            surface.blit(font_lbl.render(line, True, (255, 255, 255)), (20, y_offset))
            y_offset += 22

        if self.coupling_severed:
            win_msg = font_prompt.render("COUPLING SEVERED! DECOUPLING...", True, (255, 255, 255))
            surface.blit(win_msg, (surface.get_width() // 2 - win_msg.get_width() // 2, 240))


class DetachmentScene(LayeredScene):
    def __init__(self):
        super().__init__()
        self.logic_layer = DetachmentGameLayer()
        self.add_layer(self.logic_layer)

    def on_enter(self):
        self.logic_layer.on_enter()

    def reset(self):
        self.logic_layer.reset()
