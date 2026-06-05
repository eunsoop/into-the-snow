import pygame
from pygame.locals import *

from entity.enemy import Guard, Bullet
from scene import LayeredScene, GameLayer
from scene.tail_workshop_scene import Player


class GreenhouseGameLayer(GameLayer):
    def __init__(self):
        super().__init__()
        self.player = Player(50, 300)
        self.guards = [Guard(300, 200, 200, 500), Guard(500, 400, 400, 700)]
        self.bullets = []
        self.door_rect = pygame.Rect(0, 0, 50, 100)
        self.door_rect.center = (900, 300)
        
        self.add_entity(self.player)
        for g in self.guards:
            self.add_entity(g)

    def event(self, event):
        super().event(event)
        if event.type == KEYDOWN and event.key == K_SPACE:
            if getattr(self.player, 'has_stun_gun', False):
                b = Bullet(self.player.x + self.player.width, self.player.y + self.player.height//2, 1, 0)
                self.bullets.append(b)
                self.add_entity(b)
        
        if event.type == KEYDOWN and event.key == K_e:
            if self.player.rect.colliderect(self.door_rect) and getattr(self.player, 'has_hack_tool', False):
                pass 

    def update(self):
        for b in self.bullets[:]:
            for g in self.guards:
                if not g.is_stunned and b.rect.colliderect(g.rect):
                    g.is_stunned = True
                    self.remove_entity(b)
                    if b in self.bullets:
                        self.bullets.remove(b)
                    break
        for g in self.guards:
            if not g.is_stunned and self.player.rect.colliderect(g.rect):
                pass 
                
    def paint(self, surface: pygame.Surface):
        super().paint(surface)
        pygame.draw.rect(surface, (150, 75, 0), self.door_rect)

class GreenhouseScene(LayeredScene):
    def __init__(self):
        super().__init__()
        self.logic_layer = GreenhouseGameLayer()
        self.add_layer(self.logic_layer)
