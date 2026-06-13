import pygame

from core import LayeredScene, GameLayer, TrainShakeEffector
from entity.collectible import CollectibleItem, StolenPart
from entity.enemy import Guard
from entity.projectile import Bullet
from tilemap import TiledImage, Tilemap, Viewpoint
from ui.hud import fire_weapon_at_mouse, paint_debug_lines

class GuardedStorageGameLayer(GameLayer):

    def __init__(self):
        super().__init__()
        self.tilemap = self.setup_map(Viewpoint(0, 0, 5))
        self.player = None
        self.guards = [
            Guard(500, 200, 300, 800),
            Guard(500, 300, 300, 900),
            Guard(1800, 250, 1300, 2200),
            Guard(2400, 450, 1800, 2800)
        ]
        for g in self.guards:
            self.add_entity(g)
        self.igniter = StolenPart(1200, 200, "igniter")
        self.keychip = StolenPart(2500, 400, "keychip")
        self.add_entity(self.igniter)
        self.add_entity(self.keychip)
        self.fire_cooldown_timer = 0.15
        self.add_effector(TrainShakeEffector(base_intensity=0.5, jolt_frequency=6.0, jolt_intensity=2.0, jolt_duration=0.4))
        self.spawn_collectibles()

    def spawn_collectibles(self):
        for e in self.entities[:]:
            if isinstance(e, CollectibleItem):
                self.remove_entity(e)
        self.add_entity(CollectibleItem(900, 430, "frozen_scrap"))
        self.add_entity(CollectibleItem(1600, 200, "alpine_resin"))
        self.add_entity(CollectibleItem(2200, 430, "frozen_scrap"))
        self.add_entity(CollectibleItem(700, 250, "coal"))
        self.add_entity(CollectibleItem(1900, 430, "coal"))

    def draw_door(self, map_data, x, y):
        for dy, oy in enumerate(range(2, 5)):
            for dx, ox in enumerate(range(2, 6)):
                map_data[y + dy][x + dx] = (oy * 6 + ox, (lambda: False))

    def draw_chair(self, map_data, x, y):
        for dy, oy in enumerate(range(2, 7)):
            for dx, ox in enumerate(range(0, 2)):
                map_data[y + dy][x + dx] = (oy * 6 + ox, (lambda: False))

    def draw_window(self, map_data, x, y):
        for dy, oy in enumerate(range(5, 7)):
            for dx, ox in enumerate(range(2, 6)):
                map_data[y + dy][x + dx] = (oy * 6 + ox, (lambda: False))

    def setup_map(self, viewpoint: Viewpoint) -> Tilemap:
        """
        Set up the guarded storage room tilemap layout structure.
        :param viewpoint: Viewpoint camera mapping parameters
        :return: Initialized Tilemap object
        """
        tiles_surf = pygame.image.load("assets/images/tilemap/tilemap.png").convert_alpha()
        tiled_image = TiledImage(tiles_surf, tile_size=8)
        map_data = {}
        for y in range(0, 4):
            map_data[y] = [(4, (lambda: False)) for _ in range(56)]
        self.draw_door(map_data, 2, 1)
        self.draw_door(map_data, 49, 1)
        for i in range(0, 7):
            self.draw_window(map_data, 7 + i * 6, 1)
        for y in range(4, 12):
            map_data[y] = [(2, (lambda: True)) for _ in range(56)]
        for i in range(0, 7):
            self.draw_chair(map_data, 6 + i * 3, 7)
        return Tilemap(tiled_image, map_data, viewpoint)

    def on_enter(self):
        game = self.get_game()
        self.player = game.player
        self.add_entity(self.player)
        tx = self.player.pop_transition_x()
        ty = self.player.pop_transition_y()
        if ty is not None: self.player.y = ty
        if tx is not None:
            self.player.x = tx
            self.player.rect.center = (int(self.player.x), int(self.player.y))
        if self.player.has_item("igniter") and self.igniter in self.entities:
            self.remove_entity(self.igniter)
        if self.player.has_item("keychip") and self.keychip in self.entities:
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
        self.spawn_collectibles()

    def event(self, event):
        super().event(event)

    def update(self):
        super().update()
        dt = self.get_game().get_dt()
        if self.player.has_item("ak47"):
            fire_weapon_at_mouse(self, dt)
        for e in self.entities[:]:
            if isinstance(e, CollectibleItem):
                if self.player.rect.colliderect(e.rect):
                    self.player.add_item(e.item_type, 1)
                    self.remove_entity(e)
        if self.player.x < 15:
            self.player.transition_x = 2000
            self.remove_entity(self.player)
            self.game.set_scene("ingame.tailworkshop")
            return
        for e in self.entities[:]:
            if isinstance(e, StolenPart):
                if self.player.rect.colliderect(e.rect):
                    if e.part_type == "igniter":
                        self.player.add_item("igniter")
                    elif e.part_type == "keychip":
                        self.player.add_item("keychip")
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
        """
        Draw the guarded storage game environment layer and debug HUD stats.
        :param surface: The destination drawing pygame.Surface
        """
        super().paint(surface)
        lines = [
            f"X: {int(self.player.x)} Y: {int(self.player.y)}",
            f"CamX: {int(self.tilemap.viewpoint.x)} CamY: {int(self.tilemap.viewpoint.y)}",
            f"HP: {int(self.player.health)}",
            f"Temp: {int(self.player.temperature)}",
            f"Scrap: {self.player.get_item_count('frozen_scrap')}",
            f"Resin: {self.player.get_item_count('alpine_resin')}",
            f"Coal: {self.player.get_item_count('coal')}",
            f"Igniter: {self.player.has_item('igniter')}",
            f"Keychip: {self.player.has_item('keychip')}",
            f"Medkit: {self.player.get_item_count('medkit')}",
            f"Thermopack: {self.player.get_item_count('thermopack')}"
        ]
        paint_debug_lines(surface, lines)

class GuardedStorageScene(LayeredScene):
    def __init__(self):
        super().__init__()
        self.game_layer = GuardedStorageGameLayer()
        self.add_layer(self.game_layer)

    def on_enter(self):
        self.game_layer.on_enter()

    def reset(self):
        self.game_layer.reset()

