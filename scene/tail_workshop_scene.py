from pygame.locals import *

from entity.player import Player
from entity.stationary import CraftingTable, Furnace, Hatch
from scene import LayeredScene, GameLayer


class TailWorkshopGameLayer(GameLayer):
    def __init__(self):
        super().__init__()
        self.player = Player(100, 100)
        self.furnace = Furnace(50, 50)
        self.crafting_table = CraftingTable(400, 50)
        self.hatch = Hatch(400, 500)
        
        self.add_entity(self.player)
        self.add_entity(self.furnace)
        self.add_entity(self.crafting_table)
        self.add_entity(self.hatch)

    def event(self, event):
        super().event(event)
        if event.type == KEYDOWN and event.key == K_e:
            if self.player.rect.colliderect(self.furnace.rect):
                if self.player.wood > 0:
                    self.player.wood -= 1
                    self.player.temperature = min(100.0, self.player.temperature + 20.0)
            
            if self.player.rect.colliderect(self.crafting_table.rect):
                if self.player.wood >= 5 and self.player.scrap >= 3:
                    self.player.has_stun_gun = True
                    self.player.has_hack_tool = True
                    self.player.wood -= 5
                    self.player.scrap -= 3

    def update_logic(self):
        if self.player.rect.colliderect(self.hatch.rect):
            pass 

class TailWorkshopScene(LayeredScene):
    def __init__(self):
        super().__init__()
        self.logic_layer = TailWorkshopGameLayer()
        self.add_layer(self.logic_layer)
