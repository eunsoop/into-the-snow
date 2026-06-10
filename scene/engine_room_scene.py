import pygame
from pygame.locals import *

from entity import Entity
from entity.player import Player
from entity.enemy import Boss
from entity.projectile import Bullet
from core import LayeredScene, GameLayer, Fonts
from tilemap import TiledImage, Tilemap, Viewpoint


class BrokenEngineCore(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.is_solid = True
        self.rect = pygame.Rect(0, 0, 96, 128)
        self.rect.center = (int(self.x), int(self.y))

    def paint(self, surface: pygame.Surface):
        color = (50, 50, 50)
        border_color = (255, 50, 50)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 3)
        pygame.draw.circle(surface, (150, 50, 50), self.rect.center, 16)


class EngineRoomGameLayer(GameLayer):
    def __init__(self):
        super().__init__()
        
        tiles_surf = pygame.Surface((64, 32))
        pygame.draw.rect(tiles_surf, (25, 25, 40), (0, 0, 32, 32))
        pygame.draw.rect(tiles_surf, (10, 10, 25), (0, 0, 32, 32), 2)
        pygame.draw.rect(tiles_surf, (75, 75, 90), (32, 0, 32, 32))
        pygame.draw.rect(tiles_surf, (55, 55, 70), (32, 0, 32, 32), 1)
        
        tiled_image = TiledImage(tiles_surf, tile_size=32)
        
        map_data = {}
        for y in range(22):
            row = []
            for x in range(32):
                is_border = (x == 0 or y == 0 or y == 21)
                tile_type = 0 if is_border else 1
                passable = (lambda: False) if is_border else (lambda: True)
                row.append((tile_type, passable))
            map_data[y] = row
            
        viewpoint = Viewpoint(0, 0, 3.0)
        self.tilemap = Tilemap(tiled_image, map_data, viewpoint)
        
        self.engine = BrokenEngineCore(200, 300)
        self.tilemap.add_stationary(self.engine)
        
        self.player = Player(2800, 300)
        self.add_entity(self.player)
        
        self.boss = None
        self.engine_repaired = False
        self.detachment_timer = 30.0

    def on_enter(self):
        game = self.get_game()
        self.player.temperature = game.player_data["temperature"]
        self.player.health = game.player_data["health"]
        self.player.frozen_scrap = game.player_data["frozen_scrap"]
        self.player.alpine_resin = game.player_data["alpine_resin"]
        self.player.has_igniter = game.player_data["has_igniter"]
        self.player.has_keychip = game.player_data["has_keychip"]
        self.player.has_stun_gun = game.player_data["has_stun_gun"]
        
        self.engine_repaired = game.player_data["engine_repaired"]
        self.detachment_timer = game.player_data["detachment_timer"]
        
        if self.engine_repaired:
            if self.boss not in self.entities and game.player_data["boss_hp"] > 0:
                self.boss = Boss(2400, 300, 100, 600)
                self.boss.hp = game.player_data["boss_hp"]
                self.add_entity(self.boss)

    def save_player_data(self):
        game = self.get_game()
        game.player_data["temperature"] = self.player.temperature
        game.player_data["health"] = self.player.health
        game.player_data["frozen_scrap"] = self.player.frozen_scrap
        game.player_data["alpine_resin"] = self.player.alpine_resin
        game.player_data["has_igniter"] = self.player.has_igniter
        game.player_data["has_keychip"] = self.player.has_keychip
        game.player_data["has_stun_gun"] = self.player.has_stun_gun
        
        game.player_data["engine_repaired"] = self.engine_repaired
        game.player_data["detachment_timer"] = self.detachment_timer
        if self.boss in self.entities:
            game.player_data["boss_hp"] = self.boss.hp
        else:
            game.player_data["boss_hp"] = 0

    def event(self, event):
        super().event(event)
        
        if event.type == KEYDOWN and event.key == K_SPACE:
            if self.player.has_stun_gun:
                b = Bullet(self.player.x + 24, self.player.y, 1.0, 0.0, is_enemy=False)
                b.speed = 350
                self.add_entity(b)

        if event.type == KEYDOWN and event.key == K_e:
            if self.player.rect.colliderect(self.engine.rect):
                if not self.engine_repaired:
                    if (self.player.frozen_scrap >= 3 and 
                        self.player.alpine_resin >= 2 and 
                        self.player.has_igniter and 
                        self.player.has_keychip):
                        
                        self.player.frozen_scrap -= 3
                        self.player.alpine_resin -= 2
                        self.engine_repaired = True
                        self.detachment_timer = 30.0
                        
                        self.boss = Boss(2400, 300, 100, 600)
                        self.add_entity(self.boss)

    def update(self):
        super().update()
        dt = self.get_game().get_dt()
        
        if self.player.x > 2900:
            self.save_player_data()
            self.game.player_data["transition_x"] = 100
            self.game.set_scene("ingame.tailworkshop")
            return

        if self.engine_repaired:
            self.detachment_timer -= dt
            if self.detachment_timer <= 0:
                self.detachment_timer = 0
                self.save_player_data()
                self.game.set_scene("gamewin")
                return

        bullets = [e for e in self.entities if isinstance(e, Bullet)]
        for b in bullets:
            if b.is_enemy:
                if b.rect.colliderect(self.player.rect):
                    self.player.health = max(0.0, self.player.health - 15.0)
                    if b in self.entities:
                        self.remove_entity(b)
            else:
                if self.boss in self.entities and b.rect.colliderect(self.boss.rect):
                    self.boss.hp -= 10
                    if b in self.entities:
                        self.remove_entity(b)
                    
                    if self.boss.hp <= 0:
                        self.remove_entity(self.boss)
                    break

    def paint(self, surface: pygame.Surface):
        super().paint(surface)
        
        font = Fonts.Jersey_10(20)
        
        boss_hp_str = str(self.boss.hp) if (self.boss and self.boss in self.entities) else "0"
        timer_str = str(int(self.detachment_timer)) if self.engine_repaired else "30"
        
        lines = [
            f"X: {int(self.player.x)} Y: {int(self.player.y)}",
            f"CamX: {int(self.tilemap.viewpoint.x)} CamY: {int(self.tilemap.viewpoint.y)}",
            f"HP: {int(self.player.health)}",
            f"Temp: {int(self.player.temperature)}",
            f"Engine: {self.engine_repaired}",
            f"Time: {timer_str}",
            f"Boss: {boss_hp_str}"
        ]
        
        y_offset = 20
        for line in lines:
            if line:
                surface.blit(font.render(line, True, (255, 255, 255)), (20, y_offset))
                y_offset += 22


class EngineRoomScene(LayeredScene):
    def __init__(self):
        super().__init__()
        self.logic_layer = EngineRoomGameLayer()
        self.add_layer(self.logic_layer)

    def on_enter(self):
        self.logic_layer.on_enter()
