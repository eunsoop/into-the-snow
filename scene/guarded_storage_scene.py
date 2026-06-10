import pygame
from pygame.locals import *

from core import LayeredScene, GameLayer, Fonts, ShakeEffector
from entity import Entity
from entity.enemy import Guard
from entity.projectile import Bullet
from tilemap import TiledImage, Tilemap, Viewpoint


class StolenPart(Entity):
    def __init__(self, x: float, y: float, part_type: str):
        super().__init__(x, y)
        self.part_type = part_type
        self.rect = pygame.Rect(0, 0, 24, 24)
        self.rect.center = (int(self.x), int(self.y))

    def paint(self, surface: pygame.Surface):
        color = (255, 165, 0) if self.part_type == "igniter" else (0, 255, 255)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)


class GuardedStorageGameLayer(GameLayer):
    def __init__(self):
        super().__init__()
        
        tiles_surf = pygame.Surface((64, 32))
        pygame.draw.rect(tiles_surf, (40, 45, 40), (0, 0, 32, 32))
        pygame.draw.rect(tiles_surf, (20, 25, 20), (0, 0, 32, 32), 2)
        pygame.draw.rect(tiles_surf, (110, 100, 90), (32, 0, 32, 32))
        pygame.draw.rect(tiles_surf, (90, 80, 70), (32, 0, 32, 32), 1)
        
        tiled_image = TiledImage(tiles_surf, tile_size=32)
        
        map_data = {}
        for y in range(22):
            row = []
            for x in range(32):
                is_border = (x == 31 or y == 0 or y == 21)
                tile_type = 0 if is_border else 1
                passable = (lambda: False) if is_border else (lambda: True)
                row.append((tile_type, passable))
            map_data[y] = row
            
        viewpoint = Viewpoint(0, 0, 3.0)
        self.tilemap = Tilemap(tiled_image, map_data, viewpoint)
        
        self.player = None
        
        self.guards = [
            Guard(500, 200, 300, 800),
            Guard(1100, 400, 700, 1400),
            Guard(1800, 250, 1300, 2200),
            Guard(2400, 450, 1800, 2800)
        ]
        for g in self.guards:
            self.add_entity(g)

        self.igniter = StolenPart(1200, 200, "igniter")
        self.keychip = StolenPart(2500, 400, "keychip")
        self.add_entity(self.igniter)
        self.add_entity(self.keychip)

    def on_enter(self):
        game = self.get_game()
        self.player = game.player
        self.add_entity(self.player)

        tx = self.player.pop_transition_x()
        if tx is not None:
            self.player.x = tx
            self.player.rect.center = (int(self.player.x), int(self.player.y))

        if self.player.has_igniter and self.igniter in self.entities:
            self.remove_entity(self.igniter)
        if self.player.has_keychip and self.keychip in self.entities:
            self.remove_entity(self.keychip)

    def reset(self):
        if self.player and self.player in self.entities:
            self.remove_entity(self.player)
        self.player = None
        bullets = [e for e in self.entities if isinstance(e, Bullet)]
        for b in bullets:
            self.remove_entity(b)
        for g in self.guards:
            if g in self.entities:
                self.remove_entity(g)
        self.guards = [
            Guard(500, 200, 300, 800),
            Guard(1100, 400, 700, 1400),
            Guard(1800, 250, 1300, 2200),
            Guard(2400, 450, 1800, 2800)
        ]
        for g in self.guards:
            self.add_entity(g)
        if self.igniter in self.entities:
            self.remove_entity(self.igniter)
        if self.keychip in self.entities:
            self.remove_entity(self.keychip)
        self.igniter = StolenPart(1200, 200, "igniter")
        self.keychip = StolenPart(2500, 400, "keychip")
        self.add_entity(self.igniter)
        self.add_entity(self.keychip)

    def event(self, event):
        super().event(event)
        
        if event.type == KEYDOWN and event.key == K_SPACE:
            if self.player.has_stun_gun:
                b = Bullet(self.player.x + 24, self.player.y, 1.0, 0.0, is_enemy=False)
                b.speed = 350
                self.add_entity(b)
                self.add_effector(ShakeEffector(duration=0.15, intensity=3.0))

    def update(self):
        super().update()
        dt = self.get_game().get_dt()

        if self.player.x < 15:
            self.player.transition_x = 2800
            self.remove_entity(self.player)
            self.game.set_scene("ingame.tailworkshop")
            return

        for e in self.entities[:]:
            if isinstance(e, StolenPart):
                if self.player.rect.colliderect(e.rect):
                    if e.part_type == "igniter":
                        self.player.has_igniter = True
                    elif e.part_type == "keychip":
                        self.player.has_keychip = True
                    self.remove_entity(e)

        bullets = [e for e in self.entities if isinstance(e, Bullet)]
        for b in bullets:
            for g in self.guards:
                if not g.is_stunned and b.rect.colliderect(g.rect):
                    g.is_stunned = True
                    g.stun_timer = 0.0
                    if b in self.entities:
                        self.remove_entity(b)
                    break

        for g in self.guards:
            if not g.is_stunned and self.player.rect.colliderect(g.los_rect):
                self.player.health = max(10.0, self.player.health - 20.0)
                self.player.transition_x = 1000
                self.player.spotted_shake = True
                self.remove_entity(self.player)
                self.game.set_scene("ingame.tailworkshop")
                return

    def paint(self, surface: pygame.Surface):
        super().paint(surface)
        
        font = Fonts.Jersey_10(20)
        lines = [
            f"X: {int(self.player.x)} Y: {int(self.player.y)}",
            f"CamX: {int(self.tilemap.viewpoint.x)} CamY: {int(self.tilemap.viewpoint.y)}",
            f"HP: {int(self.player.health)}",
            f"Temp: {int(self.player.temperature)}",
            f"Scrap: {self.player.frozen_scrap}",
            f"Resin: {self.player.alpine_resin}",
            f"Igniter: {self.player.has_igniter}",
            f"Keychip: {self.player.has_keychip}"
        ]
        
        y_offset = 20
        for line in lines:
            if line:
                surface.blit(font.render(line, True, (255, 255, 255)), (20, y_offset))
                y_offset += 22


class GuardedStorageScene(LayeredScene):
    def __init__(self):
        super().__init__()
        self.logic_layer = GuardedStorageGameLayer()
        self.add_layer(self.logic_layer)

    def on_enter(self):
        self.logic_layer.on_enter()

    def reset(self):
        self.logic_layer.reset()
