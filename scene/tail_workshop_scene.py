import random

import pygame
from pygame.locals import *

from core import LayeredScene, GameLayer, Fonts, ShakeEffector, FlashEffector, TrainShakeEffector
from entity.stationary import CraftingTable, Furnace, Hatch
from tilemap import TiledImage, Tilemap, Viewpoint


class TailWorkshopGameLayer(GameLayer):
    def __init__(self):
        super().__init__()

        self.tilemap = self.setup_map(Viewpoint(0, 0, 5))

        self.furnace = Furnace(200, 150)
        self.crafting_table = CraftingTable(900, 150)
        self.hatch = Hatch(1500, 400)
        
        # self.tilemap.add_stationary(self.furnace)
        # self.tilemap.add_stationary(self.crafting_table)
        # self.tilemap.add_stationary(self.hatch)

        self.add_effector(ShakeEffector(duration=0.1, intensity=10.0))
        
        self.player = None

        self.state = "NORMAL"
        self.scavenge_timer = 0.0
        self.scavenge_items = []
        self.scavenge_spawn_timer = 0.0
        
        self.hook_rect = pygame.Rect(500, 100, 20, 20)
        self.hook_state = "IDLE"
        self.hook_speed = 380
        
        self.add_effector(TrainShakeEffector(base_intensity=0.5, jolt_frequency=4.0, jolt_intensity=2.0, jolt_duration=0.4))

    def draw_door(self, map_data: dict, x, y):
        for dy, oy in enumerate(range(2, 5)):
            for dx, ox in enumerate(range(2, 6)):
                map_data[y+dy][x+dx] = (oy*6+ox, (lambda: False))

    def setup_map(self, viewpoint: Viewpoint) -> Tilemap:
        tiles_surf = pygame.image.load("assets/images/tilemap/tilemap.png")
        tiled_image = TiledImage(tiles_surf, tile_size=8)

        map_data = {}
        for y in range(0, 4): map_data[y] = [(4, (lambda: False)) for _ in range(30)]
        self.draw_door(map_data, 2, 1)
        self.draw_door(map_data, 24, 1)
        for y in range(4, 12): map_data[y] = [(2, (lambda: True)) for _ in range(30)]
        return Tilemap(tiled_image, map_data, viewpoint)

    def on_enter(self):
        game = self.get_game()
        self.player = game.player
        self.add_entity(self.player)

        tx = self.player.pop_transition_x()
        if tx is not None:
            self.player.x = tx
            self.player.rect.center = (int(self.player.x), int(self.player.y))

        if self.player.pop_spotted_shake():
            self.add_effector(ShakeEffector(duration=0.5, intensity=15.0))
            self.add_effector(FlashEffector(duration=0.25, color=(255, 0, 0), max_alpha=180))

    def reset(self):
        if self.player and self.player in self.entities:
            self.remove_entity(self.player)
        self.player = None
        self.state = "NORMAL"
        self.scavenge_items.clear()
        self.hook_state = "IDLE"
        self.hook_rect.y = 100

    def event(self, event):
        if self.state == "SCAVENGE":
            if event.type == KEYDOWN and event.key == K_SPACE:
                if self.hook_state == "IDLE":
                    self.hook_state = "LAUNCH"
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.exit_scavenge()
            return
            
        super().event(event)
        
        if event.type == KEYDOWN and event.key == K_e:
            if self.player.rect.colliderect(self.furnace.rect):
                if self.player.get_item_count("frozen_scrap") > 0:
                    self.player.remove_item("frozen_scrap", 1)
                    self.player.temperature = 100.0
            
            if self.player.rect.colliderect(self.crafting_table.rect):
                if not self.player.has_item("stun_gun"):
                    if self.player.get_item_count("frozen_scrap") >= 1 and self.player.get_item_count("alpine_resin") >= 1:
                        self.player.add_item("stun_gun")
                        self.player.remove_item("frozen_scrap", 1)
                        self.player.remove_item("alpine_resin", 1)

    def start_scavenge(self):
        self.state = "SCAVENGE"
        self.scavenge_timer = 15.0
        self.scavenge_items.clear()
        self.hook_rect.x = 490
        self.hook_rect.y = 100
        self.hook_state = "IDLE"

    def exit_scavenge(self):
        self.state = "NORMAL"
        self.player.x = 1350
        self.player.y = 400
        self.player.rect.center = (1350, 400)

    def update(self):
        dt = self.get_game().get_dt()

        if self.state == "SCAVENGE":
            self.scavenge_timer -= dt
            self.player.temperature -= 3.0 * dt
            
            if self.scavenge_timer <= 0 or self.player.health <= 0 or self.player.temperature <= 0:
                self.player.temperature = max(0.0, self.player.temperature)
                self.player.health = max(0.0, self.player.health)
                if self.player.health <= 0 or self.player.temperature <= 0:
                    self.save_player_data()
                    self.game.set_scene("gameover")
                else:
                    self.exit_scavenge()
                return

            self.scavenge_spawn_timer += dt
            if self.scavenge_spawn_timer >= 1.0:
                self.scavenge_spawn_timer = 0.0
                itype = random.choice(["scrap", "resin", "rock", "rock"])
                iy = random.randint(320, 600)
                ispeed = random.randint(180, 280)
                self.scavenge_items.append({
                    "rect": pygame.Rect(1000, iy, 24, 24),
                    "type": itype,
                    "speed": ispeed
                })

            for item in self.scavenge_items[:]:
                item["rect"].x -= item["speed"] * dt
                if item["rect"].right < 0:
                    self.scavenge_items.remove(item)

            if self.hook_state == "LAUNCH":
                self.hook_rect.y += self.hook_speed * dt
                if self.hook_rect.y >= 620:
                    self.hook_state = "RETRACT"
            elif self.hook_state == "RETRACT":
                self.hook_rect.y -= self.hook_speed * dt
                if self.hook_rect.y <= 100:
                    self.hook_rect.y = 100
                    self.hook_state = "IDLE"

            if self.hook_state == "LAUNCH":
                for item in self.scavenge_items[:]:
                    if self.hook_rect.colliderect(item["rect"]):
                        if item["type"] == "rock":
                            self.player.health = max(0.0, self.player.health - 10.0)
                            self.add_effector(ShakeEffector(duration=0.3, intensity=10.0))
                            self.add_effector(FlashEffector(duration=0.15, color=(255, 0, 0), max_alpha=128))
                            self.hook_state = "RETRACT"
                            self.scavenge_items.remove(item)
                        else:
                            if item["type"] == "scrap":
                                self.player.add_item("frozen_scrap")
                            elif item["type"] == "resin":
                                self.player.add_item("alpine_resin")
                            self.hook_state = "RETRACT"
                            self.scavenge_items.remove(item)
                        break
            return

        super().update()
        
        if self.player.x < 15:
            self.player.transition_x = 2800
            self.remove_entity(self.player)
            self.game.set_scene("ingame.engineroom")
            return
        elif self.player.x > 1905:
            self.player.transition_x = 100
            self.remove_entity(self.player)
            self.game.set_scene("ingame.guardedstorage")
            return

        if self.player.rect.colliderect(self.hatch.rect):
            self.start_scavenge()
            return

    def paint(self, surface: pygame.Surface):
        if self.state == "SCAVENGE":
            surface.fill((200, 200, 215))
            
            pygame.draw.line(surface, (150, 150, 160), (500, 80), self.hook_rect.center, 3)
            pygame.draw.rect(surface, (80, 80, 90), self.hook_rect)
            pygame.draw.rect(surface, (255, 255, 255), self.hook_rect, 1)

            for item in self.scavenge_items:
                if item["type"] == "scrap":
                    color = (170, 170, 180)
                elif item["type"] == "resin":
                    color = (0, 220, 120)
                else:
                    color = (80, 80, 80)
                pygame.draw.rect(surface, color, item["rect"])
                pygame.draw.rect(surface, (255, 255, 255), item["rect"], 1)

            font = Fonts.Jersey_10(20)
            lines = [
                f"Time: {int(self.scavenge_timer)}",
                f"HP: {int(self.player.health)}",
                f"Temp: {int(self.player.temperature)}",
                f"Scrap: {self.player.get_item_count('frozen_scrap')}",
                f"Resin: {self.player.get_item_count('alpine_resin')}"
            ]
            y_offset = 20
            for line in lines:
                if line:
                    surface.blit(font.render(line, True, (20, 20, 30)), (20, y_offset))
                    y_offset += 22
            return

        super().paint(surface)
        
        font = Fonts.Jersey_10(20)
        lines = [
            f"X: {int(self.player.x)} Y: {int(self.player.y)}",
            f"CamX: {int(self.tilemap.viewpoint.x)} CamY: {int(self.tilemap.viewpoint.y)}",
            f"HP: {int(self.player.health)}",
            f"Temp: {int(self.player.temperature)}",
            f"Scrap: {self.player.get_item_count('frozen_scrap')}",
            f"Resin: {self.player.get_item_count('alpine_resin')}",
            f"Gun: {self.player.has_item('stun_gun')}",
            f"Igniter: {self.player.has_item('igniter')}",
            f"Keychip: {self.player.has_item('keychip')}"
        ]
        
        y_offset = 20
        for line in lines:
            if line:
                surface.blit(font.render(line, True, (255, 255, 255)), (20, y_offset))
                y_offset += 22


class TailWorkshopScene(LayeredScene):
    def __init__(self):
        super().__init__()
        self.logic_layer = TailWorkshopGameLayer()
        self.add_layer(self.logic_layer)

    def on_enter(self):
        self.logic_layer.on_enter()

    def reset(self):
        self.logic_layer.reset()
