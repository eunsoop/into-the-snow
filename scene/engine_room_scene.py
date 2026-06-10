import pygame
from pygame.locals import *

from core import LayeredScene, GameLayer, Fonts, ShakeEffector, FlashEffector
from entity import Entity
from entity.enemy import Boss
from entity.projectile import Bullet
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
        
        self.player = None
        self.boss = None
        self.engine_repaired = False
        self.detachment_timer = 30.0
        self.boss_hp = 100

    def on_enter(self):
        game = self.get_game()
        self.player = game.player
        self.add_entity(self.player)
        
        tx = self.player.pop_transition_x()
        if tx is not None:
            self.player.x = tx
            self.player.rect.center = (int(self.player.x), int(self.player.y))
        
        if self.engine_repaired:
            if self.boss not in self.entities and self.boss_hp > 0:
                self.boss = Boss(2400, 300, 100, 600)
                self.boss.hp = self.boss_hp
                self.add_entity(self.boss)

    def reset(self):
        if self.player and self.player in self.entities:
            self.remove_entity(self.player)
        self.player = None
        self.engine_repaired = False
        self.detachment_timer = 30.0
        self.boss_hp = 100
        if self.boss in self.entities:
            self.remove_entity(self.boss)
        self.boss = None
        bullets = [e for e in self.entities if isinstance(e, Bullet)]
        for b in bullets:
            self.remove_entity(b)

    def event(self, event):
        super().event(event)
        
        if event.type == KEYDOWN and event.key == K_SPACE:
            if self.player.has_stun_gun:
                b = Bullet(self.player.x + 24, self.player.y, 1.0, 0.0, is_enemy=False)
                b.speed = 350
                self.add_entity(b)
                self.add_effector(ShakeEffector(duration=0.15, intensity=3.0))

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
            self.player.transition_x = 100
            self.remove_entity(self.player)
            self.game.set_scene("ingame.tailworkshop")
            return

        if self.engine_repaired:
            self.detachment_timer -= dt
            if self.detachment_timer <= 0:
                self.detachment_timer = 0
                self.remove_entity(self.player)
                self.game.set_scene("gamewin")
                return

        bullets = [e for e in self.entities if isinstance(e, Bullet)]
        for b in bullets:
            if b.is_enemy:
                if b.rect.colliderect(self.player.rect):
                    self.player.health = max(0.0, self.player.health - 15.0)
                    self.add_effector(ShakeEffector(duration=0.3, intensity=10.0))
                    self.add_effector(FlashEffector(duration=0.15, color=(255, 0, 0), max_alpha=128))
                    if b in self.entities:
                        self.remove_entity(b)
            else:
                if self.boss in self.entities and b.rect.colliderect(self.boss.rect):
                    self.boss.hp -= 10
                    self.boss_hp = self.boss.hp
                    if b in self.entities:
                        self.remove_entity(b)
                    
                    if self.boss.hp <= 0:
                        self.remove_entity(self.boss)
                        self.boss_hp = 0
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

    def reset(self):
        self.logic_layer.reset()
