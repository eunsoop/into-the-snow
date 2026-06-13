import random
import math

import pygame
from pygame.locals import *

from core import LayeredScene, GameLayer, Fonts, ShakeEffector, FlashEffector, TrainShakeEffector
from entity.projectile import Bullet
from entity.enemy import DetachmentBoss
from scene.background_layers import WeightedBackgroundLayer
from tilemap import TiledImage, Tilemap, Viewpoint
from ui.hud import paint_debug_lines

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
        """Create grid representation of left and right carriage platforms."""
        tiles_surf = pygame.image.load("assets/images/tilemap/tilemap.png").convert_alpha()
        tiled_image = TiledImage(tiles_surf, tile_size=8)
        map_data = {}
        for y in range(5, 16):
            row = []
            for x in range(25):
                is_left_car_floor = (y == 14 and x < 8)
                is_right_car_floor = (y == 14 and x >= 18)
                is_left_wall = (x == 0 and y < 14)
                is_right_wall = (x == 24 and y < 14)
                if is_left_car_floor or is_right_car_floor:
                    row.append((4, lambda: False))
                elif is_left_wall or is_right_wall:
                    row.append((4, lambda: False))
                else:
                    row.append((43, lambda: True))
            map_data[y] = row
        return Tilemap(tiled_image, map_data, viewpoint)

    def on_enter(self):
        game = self.get_game()
        self.player = game.player
        self.add_entity(self.player)
        tx = self.player.pop_transition_x()
        ty = self.player.pop_transition_y()
        if tx is not None:self.player.x = tx
        if ty is not None:self.player.y = ty
        self.player.y = 344.0
        self.player.rect.center = (int(self.player.x), int(self.player.y))
        self.player_vx = 0.0
        self.player_vy = 0.0
        self.player_on_ground = True
        
        engine_room = self.game.scenes["ingame.engineroom"].game_layer
        if engine_room.engine_repaired and not self.coupling_severed:
            self.combat_active = True
            self.add_effector(FlashEffector(duration=0.5, color=(255, 0, 0), max_alpha=100))
            if not self.boss_spawned:
                self.boss_spawned = True
                self.boss = DetachmentBoss(800, 344)
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
                self.game.set_scene("outro")
                return
            self.player.x = max(100.0, min(800.0, self.player.x))
        elif self.combat_active:
            self.player.x = max(100.0, min(900.0, self.player.x))
        else:

            if self.player.x < 15:
                self.player.transition_x = 300
                self.player.transition_y = 400
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
        
        if self.player.x <= 300.0 and self.player.y + 16.0 >= 562.0 and self.player_vy >= 0:
            self.player.y = 542.0
            self.player_vy = 0.0
            self.player_on_ground = True
        right_limit = 700.0 + self.separation_offset
        if self.player.x >= right_limit and self.player.y + 16.0 >= 562.0 and self.player_vy >= 0:
            self.player.y = 542.0
            self.player_vy = 0.0
            self.player_on_ground = True
        if not self.coupling_severed:

            if 380.0 <= self.player.x <= 620.0 and self.player.y + 16.0 >= 502.0 and self.player.y + 16.0 - self.player_vy * dt <= 540.0 and self.player_vy >= 0:
                self.player.y = 485.0
                self.player_vy = 0.0
                self.player_on_ground = True
                
        self.player.rect.centery = int(self.player.y)
        if self.player.y > 600.0:
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
        """
        Draw the detachment layer including snow particles, tiles, and player/enemy blocks.
        :param surface: The destination drawing pygame.Surface
        """
        self.update()
        for e in self.entities:
            e.update()
        viewpoint = self.tilemap.viewpoint
        viewpoint.x = 0
        viewpoint.y = 110
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
                
        vx, vy = viewpoint.x, viewpoint.y + 200
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
        lines = [
            f"HP: {int(self.player.health)}",
            f"Temp: {int(self.player.temperature)}"
        ]
        if self.combat_active:
            boss_hp_str = str(self.boss.hp) if (self.boss and self.boss in self.entities) else "DESTROYED"
            lines.append(f"Boss: {boss_hp_str}")
        paint_debug_lines(surface, lines)
        if self.coupling_severed:
            win_msg = font_prompt.render("COUPLING SEVERED! DECOUPLING...", True, (255, 255, 255))
            surface.blit(win_msg, (surface.get_width() // 2 - win_msg.get_width() // 2, 240))

class DetachmentScene(LayeredScene):

    def __init__(self):
        super().__init__()
        self.bg_layer = WeightedBackgroundLayer(
            [
                (f"assets/images/background/detach/{i}.png", 0.4*(5-i)) for i in range(5, 1, -1)
            ],
            -380,
            2
        )
        self.game_layer = DetachmentGameLayer()
        self.add_layer(self.bg_layer)
        self.add_layer(self.game_layer)

    def on_enter(self):
        self.game_layer.on_enter()

    def paint(self, surface: pygame.Surface):
        super().paint(surface)
        self.bg_layer.tick()

    def reset(self):
        self.game_layer.reset()

