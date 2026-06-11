import pygame
from pygame.locals import *

from core import LayeredScene, GameLayer, Fonts, ShakeEffector, FlashEffector, TrainShakeEffector
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
        
        self.tilemap = self.setup_map(Viewpoint(0, 0, 5))
        
        self.engine = BrokenEngineCore(200, 300)
        self.tilemap.add_stationary(self.engine)
        
        self.player = None
        self.boss = None
        self.engine_repaired = False
        self.detachment_timer = 30.0
        self.boss_hp = 100
        
        self.add_effector(TrainShakeEffector(base_intensity=0.5, jolt_frequency=5.0, jolt_intensity=2.0, jolt_duration=0.4))

    def draw_door(self, map_data: dict, x, y):
        for dy, oy in enumerate(range(2, 5)):
            for dx, ox in enumerate(range(2, 6)):
                map_data[y+dy][x+dx] = (oy*6+ox, (lambda: False))

    def setup_map(self, viewpoint: Viewpoint) -> Tilemap:
        tiles_surf = pygame.image.load("assets/images/tilemap/tilemap.png")
        tiled_image = TiledImage(tiles_surf, tile_size=8)

        map_data = {}
        for y in range(0, 4): map_data[y] = [(4, (lambda: False)) for _ in range(80)]
        self.draw_door(map_data, 2, 1)
        self.draw_door(map_data, 74, 1)
        for y in range(4, 12): map_data[y] = [(2, (lambda: True)) for _ in range(80)]
        return Tilemap(tiled_image, map_data, viewpoint)

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
            if self.player.has_item("stun_gun"):
                b = Bullet(self.player.x + 24, self.player.y, 1.0, 0.0, is_enemy=False)
                b.speed = 350
                self.add_entity(b)
                self.add_effector(ShakeEffector(duration=0.15, intensity=3.0))

        if event.type == KEYDOWN and event.key == K_e:
            if self.player.rect.colliderect(self.engine.rect):
                if not self.engine_repaired:
                    if (self.player.get_item_count("frozen_scrap") >= 3 and 
                        self.player.get_item_count("alpine_resin") >= 2 and 
                        self.player.has_item("igniter") and 
                        self.player.has_item("keychip")):
                        
                        self.player.remove_item("frozen_scrap", 3)
                        self.player.remove_item("alpine_resin", 2)
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
