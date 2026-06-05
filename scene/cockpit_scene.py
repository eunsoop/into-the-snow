from pygame.locals import *

from entity.enemy import Boss
from scene import LayeredScene, GameLayer
from scene.greenhouse_scene import Bullet
from scene.tail_workshop_scene import Player


class CockpitGameLayer(GameLayer):
    def __init__(self):
        super().__init__()
        self.player = Player(100, 300)
        self.boss = Boss(800, 300, 100, 600)
        self.bullets = []
        self.boss_bullets = []
        self.boss_shoot_timer = 0.0
        
        self.add_entity(self.player)
        self.add_entity(self.boss)

    def event(self, event):
        super().event(event)
        if event.type == KEYDOWN and event.key == K_SPACE:
            if getattr(self.player, 'has_stun_gun', False):
                b = Bullet(self.player.x + self.player.width, self.player.y + self.player.height//2, 1, 0)
                self.bullets.append(b)
                self.add_entity(b)

    def update(self):
        if not self.get_game(): return
        dt = self.get_game().get_dt()
        self.boss_shoot_timer += dt
        
        if self.boss_shoot_timer >= 1.0:
            self.boss_shoot_timer = 0.0
            bb = Bullet(self.boss.x, self.boss.y + self.boss.height//2, -1, 0)
            bb.speed = 200
            self.boss_bullets.append(bb)
            self.add_entity(bb)
            
        for b in self.bullets[:]:
            if b.rect.colliderect(self.boss.rect):
                self.boss.hp -= 10
                self.remove_entity(b)
                self.bullets.remove(b)
                if self.boss.hp <= 0:
                    pass 
                    
        for bb in self.boss_bullets[:]:
            if bb.rect.colliderect(self.player.rect):
                self.player.temperature -= 20 
                self.remove_entity(bb)
                self.boss_bullets.remove(bb)
                if self.player.temperature <= 0:
                    pass 

class CockpitScene(LayeredScene):
    def __init__(self):
        super().__init__()
        self.logic_layer = CockpitGameLayer()
        self.add_layer(self.logic_layer)
