import pygame
from pygame.locals import *

from core import LayeredScene, GameLayer, Fonts, ShakeEffector, FlashEffector, TrainShakeEffector
from entity.collectible import CollectibleItem
from entity.stationary import BrokenEngineCore
from tilemap import TiledImage, Tilemap, Viewpoint
from ui.hud import fire_weapon_at_mouse, paint_debug_lines

class EngineRoomGameLayer(GameLayer):

    def __init__(self):
        super().__init__()
        self.tilemap = self.setup_map(Viewpoint(0, 0, 5))
        self.engine = BrokenEngineCore(200, 300)
        self.tilemap.add_stationary(self.engine)
        self.player = None
        self.engine_repaired = False
        self.engine_scrap = 0
        self.engine_resin = 0
        self.engine_igniter = False
        self.engine_keychip = False
        self.fire_cooldown_timer = 0.15
        self.add_effector(TrainShakeEffector(base_intensity=0.5, jolt_frequency=5.0, jolt_intensity=2.0, jolt_duration=0.4))
        self.spawn_collectibles()

    def spawn_collectibles(self):
        for e in self.entities[:]:
            if isinstance(e, CollectibleItem):
                self.remove_entity(e)
        self.add_entity(CollectibleItem(500, 250, "frozen_scrap"))
        self.add_entity(CollectibleItem(1100, 430, "alpine_resin"))
        self.add_entity(CollectibleItem(1800, 200, "alpine_resin"))
        self.add_entity(CollectibleItem(800, 300, "coal"))
        self.add_entity(CollectibleItem(1500, 430, "coal"))

    def draw_door(self, map_data, x, y):

        for dy, oy in enumerate(range(2, 5)):
            for dx, ox in enumerate(range(2, 6)):
                map_data[y + dy][x + dx] = (oy * 6 + ox, (lambda: False))

    def setup_map(self, viewpoint: Viewpoint) -> Tilemap:
        """
        Create and load the tilemap environment structure for the engine room.
        :param viewpoint: Viewpoint camera parameters
        :return: Initialized Tilemap object
        """
        tiles_surf = pygame.image.load("assets/images/tilemap/tilemap.png").convert_alpha()
        tiled_image = TiledImage(tiles_surf, tile_size=8)
        map_data = {}
        for y in range(0, 4):
            map_data[y] = [(4, (lambda: False)) for _ in range(20)]
        self.draw_door(map_data, 2, 1)
        for y in range(4, 12):
            map_data[y] = [(2, (lambda: True)) for _ in range(20)]
        return Tilemap(tiled_image, map_data, viewpoint)

    def on_enter(self):
        game = self.get_game()
        self.player = game.player
        self.add_entity(self.player)
        tx = self.player.pop_transition_x()
        ty = self.player.pop_transition_y()
        if tx is not None:
            self.player.x = tx
            self.player.y = ty
            self.player.rect.center = (int(self.player.x), int(self.player.y))

    def reset(self):
        if self.player and self.player in self.entities:
            self.remove_entity(self.player)
        self.player = None
        self.engine_repaired = False
        self.engine_scrap = 0
        self.engine_resin = 0
        self.engine_igniter = False
        self.engine_keychip = False
        self.spawn_collectibles()

    def event(self, event):
        super().event(event)
        if event.type == KEYDOWN and event.key == K_f:

            if self.player.rect.inflate(40, 40).colliderect(self.engine.rect):
                if not self.engine_repaired:

                    if self.engine_scrap < 3 and self.player.get_item_count("frozen_scrap") >= 1:
                        self.player.remove_item("frozen_scrap", 1)
                        self.engine_scrap += 1
                        self.add_effector(ShakeEffector(duration=0.15, intensity=2.0))
                    elif self.engine_resin < 2 and self.player.get_item_count("alpine_resin") >= 1:
                        self.player.remove_item("alpine_resin", 1)
                        self.engine_resin += 1
                        self.add_effector(ShakeEffector(duration=0.15, intensity=2.0))
                    elif not self.engine_igniter and self.player.has_item("igniter"):
                        self.player.remove_item("igniter", 1)
                        self.engine_igniter = True
                        self.add_effector(ShakeEffector(duration=0.15, intensity=4.0))
                        self.add_effector(FlashEffector(duration=0.1, color=(255, 255, 255), max_alpha=100))
                    elif not self.engine_keychip and self.player.has_item("keychip"):
                        self.player.remove_item("keychip", 1)
                        self.engine_keychip = True
                        self.add_effector(ShakeEffector(duration=0.15, intensity=4.0))
                        self.add_effector(FlashEffector(duration=0.1, color=(255, 255, 255), max_alpha=100))
                    
                    if self.engine_scrap >= 3 and self.engine_resin >= 2 and self.engine_igniter and self.engine_keychip:
                        self.engine_repaired = True
                        self.player.transition_x = 100
                        self.player.transition_y = 500
                        self.remove_entity(self.player)
                        self.game.set_scene("ingame.detachment")

    def update(self):
        super().update()
        dt = self.game.get_dt()
        if self.player.has_item("ak47"):
            fire_weapon_at_mouse(self, dt)
        for e in self.entities[:]:
            if isinstance(e, CollectibleItem):
                if self.player.rect.colliderect(e.rect):
                    self.player.add_item(e.item_type, 1)
                    self.remove_entity(e)
        if self.player.x > 780:
            self.player.transition_x = 100
            self.remove_entity(self.player)
            self.game.set_scene("ingame.detachment")
            return

    def paint(self, surface: pygame.Surface):
        """
        Draw the engine room game scene layers, repair prompt status, and HUD details.
        :param surface: The destination drawing pygame.Surface
        """
        super().paint(surface)
        if not self.engine_repaired and self.player.rect.inflate(40, 40).colliderect(self.engine.rect):
            prompt_font = Fonts.Jersey_10(24)
            can_insert = (
                (self.engine_scrap < 3 and self.player.get_item_count("frozen_scrap") >= 1) or
                (self.engine_resin < 2 and self.player.get_item_count("alpine_resin") >= 1) or
                (not self.engine_igniter and self.player.has_item("igniter")) or
                (not self.engine_keychip and self.player.has_item("keychip"))
            )
            ign_status = "OK" if self.engine_igniter else "NO"
            key_status = "OK" if self.engine_keychip else "NO"
            text = f"Engine Core - Scrap: {self.engine_scrap}/3, Resin: {self.engine_resin}/2, Igniter: {ign_status}, Keychip: {key_status}"
            if can_insert:
                text += "    [F] Insert Component"
            else:
                text += "    (Need parts)"
            prompt = prompt_font.render(text, True, (255, 255, 255))
            viewpoint = self.tilemap.viewpoint
            px = self.engine.rect.centerx + viewpoint.x - prompt.get_width() // 2
            py = self.engine.rect.y + viewpoint.y - 30
            surface.blit(prompt, (px, py))
        lines = [
            f"X: {int(self.player.x)} Y: {int(self.player.y)}",
            f"CamX: {int(self.tilemap.viewpoint.x)} CamY: {int(self.tilemap.viewpoint.y)}",
            f"HP: {int(self.player.health)}",
            f"Temp: {int(self.player.temperature)}",
            f"Scrap: {self.player.get_item_count('frozen_scrap')}",
            f"Resin: {self.player.get_item_count('alpine_resin')}",
            f"Coal: {self.player.get_item_count('coal')}",
            f"Engine: {self.engine_repaired}",
            f"Medkit: {self.player.get_item_count('medkit')}",
            f"Thermopack: {self.player.get_item_count('thermopack')}"
        ]
        paint_debug_lines(surface, lines)

class EngineRoomScene(LayeredScene):

    def __init__(self):
        super().__init__()
        self.game_layer = EngineRoomGameLayer()
        self.add_layer(self.game_layer)

    def on_enter(self):
        self.game_layer.on_enter()

    def reset(self):
        self.game_layer.reset()

