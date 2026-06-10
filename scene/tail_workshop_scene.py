import random

import pygame
from pygame.locals import *

from core import LayeredScene, GameLayer, Fonts
from entity.player import Player
from entity.stationary import CraftingTable, Furnace, Hatch
from tilemap import TiledImage, Tilemap, Viewpoint


class TailWorkshopGameLayer(GameLayer):
    def __init__(self):
        super().__init__()
        
        tiles_surf = pygame.Surface((64, 32))
        pygame.draw.rect(tiles_surf, (50, 50, 60), (0, 0, 32, 32))
        pygame.draw.rect(tiles_surf, (30, 30, 40), (0, 0, 32, 32), 2)
        pygame.draw.rect(tiles_surf, (120, 120, 130), (32, 0, 32, 32))
        pygame.draw.rect(tiles_surf, (100, 100, 110), (32, 0, 32, 32), 1)
        
        tiled_image = TiledImage(tiles_surf, tile_size=32)
        
        map_data = {}
        for y in range(22):
            row = []
            for x in range(32):
                is_border = (y == 0 or y == 21)
                tile_type = 0 if is_border else 1
                passable = (lambda: False) if is_border else (lambda: True)
                row.append((tile_type, passable))
            map_data[y] = row
            
        viewpoint = Viewpoint(0, 0, 3.0)
        self.tilemap = Tilemap(tiled_image, map_data, viewpoint)
        
        self.furnace = Furnace(200, 150)
        self.crafting_table = CraftingTable(900, 150)
        self.hatch = Hatch(1500, 400)
        
        self.tilemap.add_stationary(self.furnace)
        self.tilemap.add_stationary(self.crafting_table)
        self.tilemap.add_stationary(self.hatch)
        
        self.player = Player(150, 300)
        self.add_entity(self.player)

        self.state = "NORMAL"
        self.scavenge_timer = 0.0
        self.scavenge_items = []
        self.scavenge_spawn_timer = 0.0
        
        self.hook_rect = pygame.Rect(500, 100, 20, 20)
        self.hook_state = "IDLE"
        self.hook_speed = 380

    def on_enter(self):
        game = self.get_game()
        self.player.temperature = game.player_data["temperature"]
        self.player.health = game.player_data["health"]
        self.player.frozen_scrap = game.player_data["frozen_scrap"]
        self.player.alpine_resin = game.player_data["alpine_resin"]
        self.player.has_igniter = game.player_data["has_igniter"]
        self.player.has_keychip = game.player_data["has_keychip"]
        self.player.has_stun_gun = game.player_data["has_stun_gun"]

        if "transition_x" in game.player_data:
            self.player.x = game.player_data.pop("transition_x")
            self.player.rect.center = (int(self.player.x), int(self.player.y))

        if "teleport_msg" in game.player_data:
            game.player_data.pop("teleport_msg")

    def save_player_data(self):
        game = self.get_game()
        game.player_data["temperature"] = self.player.temperature
        game.player_data["health"] = self.player.health
        game.player_data["frozen_scrap"] = self.player.frozen_scrap
        game.player_data["alpine_resin"] = self.player.alpine_resin
        game.player_data["has_igniter"] = self.player.has_igniter
        game.player_data["has_keychip"] = self.player.has_keychip
        game.player_data["has_stun_gun"] = self.player.has_stun_gun

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
                if self.player.frozen_scrap > 0:
                    self.player.frozen_scrap -= 1
                    self.player.temperature = 100.0
            
            if self.player.rect.colliderect(self.crafting_table.rect):
                if not self.player.has_stun_gun:
                    if self.player.frozen_scrap >= 1 and self.player.alpine_resin >= 1:
                        self.player.has_stun_gun = True
                        self.player.frozen_scrap -= 1
                        self.player.alpine_resin -= 1

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
                            self.hook_state = "RETRACT"
                            self.scavenge_items.remove(item)
                        else:
                            if item["type"] == "scrap":
                                self.player.frozen_scrap += 1
                            elif item["type"] == "resin":
                                self.player.alpine_resin += 1
                            self.hook_state = "RETRACT"
                            self.scavenge_items.remove(item)
                        break
            return

        super().update()
        
        if self.player.x < 15:
            self.save_player_data()
            self.game.player_data["transition_x"] = 2800
            self.game.set_scene("ingame.engineroom")
            return
        elif self.player.x > 1905:
            self.save_player_data()
            self.game.player_data["transition_x"] = 100
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
                f"Scrap: {self.player.frozen_scrap}",
                f"Resin: {self.player.alpine_resin}"
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
            f"Scrap: {self.player.frozen_scrap}",
            f"Resin: {self.player.alpine_resin}",
            f"Gun: {self.player.has_stun_gun}",
            f"Igniter: {self.player.has_igniter}",
            f"Keychip: {self.player.has_keychip}"
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
