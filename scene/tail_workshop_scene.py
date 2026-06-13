import pygame
from pygame.locals import *

from core import LayeredScene, GameLayer, Fonts, ShakeEffector, FlashEffector, TrainShakeEffector
from entity.collectible import CollectibleItem
from entity.stationary import CraftingTable, Furnace
from tilemap import TiledImage, Tilemap, Viewpoint
from ui.hud import fire_weapon_at_mouse, paint_debug_lines


class TailWorkshopGameLayer(GameLayer):
    def __init__(self):
        super().__init__()
        self.tilemap = self.setup_map(Viewpoint(0, 0, 5))
        self.furnace = Furnace(400, 220)
        self.crafting_table = CraftingTable(1000, 220)
        self.tilemap.add_stationary(self.furnace)
        self.tilemap.add_stationary(self.crafting_table)
        self.player = None
        self.state = "NORMAL"
        self.fire_cooldown_timer = 0.15
        self.add_effector(TrainShakeEffector(base_intensity=0.3, jolt_frequency=2.0, jolt_intensity=2.0, jolt_duration=0.4))
        self.spawn_collectibles()

    def spawn_collectibles(self):
        for e in self.entities[:]:
            if isinstance(e, CollectibleItem):
                self.remove_entity(e)
        self.add_entity(CollectibleItem(300, 430, "frozen_scrap"))
        self.add_entity(CollectibleItem(800, 200, "alpine_resin"))
        self.add_entity(CollectibleItem(600, 430, "alpine_resin"))
        self.add_entity(CollectibleItem(1450, 430, "frozen_scrap"))
        self.add_entity(CollectibleItem(600, 350, "coal"))
        self.add_entity(CollectibleItem(1200, 430, "coal"))

    def draw_group_of_objects(self, map_data, x, y):
        self.draw_boxes(map_data, 6+x, 4+y)
        self.draw_boxes(map_data, 1+x, 9+y)
        self.draw_objects(map_data, 4+x, 7+y)
        self.draw_boxes(map_data, 7+x, 7+y)
        self.draw_boxes(map_data, 10+x, 6+y)
        self.draw_objects(map_data, 11+x, 9+y)


    def draw_boxes(self, map_data, x, y):
        for dy, oy in enumerate(range(7, 9)):
            for dx, ox in enumerate(range(2, 4)):
                map_data[y + dy][x + dx] = (oy * 6 + ox, (lambda: False))

    def draw_objects(self, map_data, x, y):
        for dy, oy in enumerate(range(7, 9)):
            for dx, ox in enumerate(range(4, 6)):
                map_data[y + dy][x + dx] = (oy * 6 + ox, (lambda: False))

    def draw_door(self, map_data, x, y):
        for dy, oy in enumerate(range(2, 5)):
            for dx, ox in enumerate(range(2, 6)):
                map_data[y + dy][x + dx] = (oy * 6 + ox, (lambda: False))

    def setup_map(self, viewpoint: Viewpoint) -> Tilemap:
        """
        Create and configure the tilemap structure for the workshop room.
        :param viewpoint: Screen offset mapping Viewpoint instance
        :return: Initialized Tilemap object
        """
        tiles_surf = pygame.image.load("assets/images/tilemap/tilemap.png").convert_alpha()
        tiled_image = TiledImage(tiles_surf, tile_size=8)
        map_data = {}
        for y in range(0, 4):
            map_data[y] = [(4, (lambda: False)) for _ in range(56)]
        self.draw_door(map_data, 2, 1)
        self.draw_door(map_data, 49, 1)
        for y in range(4, 12):
            map_data[y] = [(2, (lambda: True)) for _ in range(56)]
        self.draw_group_of_objects(map_data, 1, 0)
        self.draw_group_of_objects(map_data, 14, 1)
        self.draw_group_of_objects(map_data, 27, 0)
        map_data[12] = [(43, (lambda: False)) for _ in range(56)]
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
        if self.player.pop_spotted_shake():
            self.add_effector(ShakeEffector(duration=0.5, intensity=15.0))
            self.add_effector(FlashEffector(duration=0.25, color=(255, 0, 0), max_alpha=180))

    def reset(self):
        if self.player and self.player in self.entities:
            self.remove_entity(self.player)
        self.player = None
        self.state = "NORMAL"
        self.spawn_collectibles()

    def event(self, event):
        """
        Handle user input keypresses and click events for workshop interactions.
        :param event: pygame.event.Event instance
        """
        if self.state == "CRAFTING":
            self.handle_menu_event(event)
            return
        if event.type == KEYDOWN and event.key == K_f:

            furnace_dist = max(abs(self.player.x - self.furnace.x), abs(self.player.y - self.furnace.y))
            crafting_dist = max(abs(self.player.x - self.crafting_table.x), abs(self.player.y - self.crafting_table.y))
            if furnace_dist < 60:
                if self.player.get_item_count("coal") >= 1:
                    if self.furnace.fuel < 100.0:
                        self.player.remove_item("coal", 1)
                        self.furnace.fuel = min(100.0, self.furnace.fuel + 50.0)
            elif crafting_dist < 60:
                self.state = "CRAFTING"
            return
        super().event(event)

    def handle_menu_event(self, event):
        if event.type == KEYDOWN:
            if event.key in (K_ESCAPE, K_f):
                self.state = "NORMAL"
                return
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            if self.state == "CRAFTING":
                container = pygame.Rect(275, 130, 450, 440)
                r1 = pygame.Rect(container.x + 20, container.y + 110, 410, 75)
                r2 = pygame.Rect(container.x + 20, container.y + 195, 410, 75)
                r3 = pygame.Rect(container.x + 20, container.y + 280, 410, 75)
                close_rect = pygame.Rect(container.x + 20, container.y + 375, 410, 45)

                if r1.collidepoint(mx, my):
                    if not self.player.has_item("ak47"):
                        if self.player.get_item_count("frozen_scrap") >= 1 and self.player.get_item_count("alpine_resin") >= 1:
                            self.player.remove_item("frozen_scrap", 1)
                            self.player.remove_item("alpine_resin", 1)
                            self.player.add_item("ak47", 1)
                elif r2.collidepoint(mx, my):
                    if self.player.get_item_count("frozen_scrap") >= 2 and self.player.get_item_count("alpine_resin") >= 2:
                        self.player.remove_item("frozen_scrap", 2)
                        self.player.remove_item("alpine_resin", 2)
                        self.player.add_item("medkit", 1)
                elif r3.collidepoint(mx, my):
                    if self.player.get_item_count("frozen_scrap") >= 1 and self.player.get_item_count("alpine_resin") >= 3:
                        self.player.remove_item("frozen_scrap", 1)
                        self.player.remove_item("alpine_resin", 3)
                        self.player.add_item("thermopack", 1)
                elif close_rect.collidepoint(mx, my):
                    self.state = "NORMAL"

    def paint_hud(self, surface: pygame.Surface):
        """
        Draw on-screen item collection/furnace prompts relative to player proximity.
        :param surface: Target drawing pygame.Surface
        """
        font = Fonts.Jersey_10(24)
        viewpoint = self.tilemap.viewpoint
        furnace_dist = max(abs(self.player.x - self.furnace.x), abs(self.player.y - self.furnace.y))
        crafting_dist = max(abs(self.player.x - self.crafting_table.x), abs(self.player.y - self.crafting_table.y))
        if furnace_dist < 60:
            fuel_pct = int(self.furnace.fuel)
            if self.player.get_item_count("coal") >= 1:
                if fuel_pct >= 100:
                    text = f"Furnace Full (Fuel: {fuel_pct}%)"
                else:
                    text = f"[F] Add Coal (Fuel: {fuel_pct}% / Coal: {self.player.get_item_count('coal')})"
            else:
                text = f"Need Coal to Refuel (Fuel: {fuel_pct}%)"
            prompt = font.render(text, True, (255, 255, 255))
            px = self.furnace.x + viewpoint.x - prompt.get_width() // 2
            py = self.furnace.y + viewpoint.y - 52
            surface.blit(prompt, (px, py))
        elif crafting_dist < 60:
            prompt = font.render("[F] Craft Items (Workbench)", True, (255, 255, 255))
            px = self.crafting_table.x + viewpoint.x - prompt.get_width() // 2
            py = self.crafting_table.y + viewpoint.y - 52
            surface.blit(prompt, (px, py))

    def paint_crafting_ui(self, surface: pygame.Surface):
        """
        Draw the interactive item crafting selection screen menu overlay.
        :param surface: Target drawing pygame.Surface
        """
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((5, 5, 5, 200))
        surface.blit(overlay, (0, 0))
        container = pygame.Rect(275, 130, 450, 440)
        pygame.draw.rect(surface, (15, 15, 15), container, border_radius=12)
        pygame.draw.rect(surface, (255, 255, 255), container, width=2, border_radius=12)
        font_title = Fonts.Jersey_10(36)
        title_surf = font_title.render("CRAFTING BENCH", True, (255, 255, 255))
        surface.blit(title_surf, (container.x + 20, container.y + 20))
        pygame.draw.line(surface, (60, 60, 60), (container.x + 20, container.y + 65), (container.right - 20, container.y + 65), 2)
        font_res = Fonts.Jersey_10(20)
        res_str = f"Your Inventory:  Scrap: {self.player.get_item_count('frozen_scrap')}   Resin: {self.player.get_item_count('alpine_resin')}"
        res_surf = font_res.render(res_str, True, (180, 180, 180))
        surface.blit(res_surf, (container.x + 20, container.y + 75))
        items = [
            {
                "name": "AK-47",
                "cost": {"frozen_scrap": 1, "alpine_resin": 1},
                "desc": "Rifle to eliminate enemies",
                "id": "ak47",
                "rect": pygame.Rect(container.x + 20, container.y + 110, 410, 75)
            },
            {
                "name": "Medkit",
                "cost": {"frozen_scrap": 2, "alpine_resin": 2},
                "desc": "Heal 40 HP (Press H to use)",
                "id": "medkit",
                "rect": pygame.Rect(container.x + 20, container.y + 195, 410, 75)
            },
            {
                "name": "Thermopack",
                "cost": {"frozen_scrap": 1, "alpine_resin": 3},
                "desc": "Restore 50 Temperature (Press T to use)",
                "id": "thermopack",
                "rect": pygame.Rect(container.x + 20, container.y + 280, 410, 75)
            }
        ]
        mx, my = pygame.mouse.get_pos()
        font_item = Fonts.Jersey_10(24)
        font_desc = Fonts.Jersey_10(16)
        for item in items:
            hovered = item["rect"].collidepoint(mx, my)
            box_color = (40, 40, 40) if hovered else (20, 20, 20)
            border_color = (255, 255, 255) if hovered else (70, 70, 70)
            pygame.draw.rect(surface, box_color, item["rect"], border_radius=6)
            pygame.draw.rect(surface, border_color, item["rect"], width=1, border_radius=6)
            owned_count = self.player.get_item_count(item["id"])
            if item["id"] == "ak47":
                owned_str = " (Owned)" if self.player.has_item("ak47") else " (Not Owned)"
            else:
                owned_str = f" (Qty: {owned_count})"
            name_surf = font_item.render(item["name"] + owned_str, True, (255, 255, 255))
            desc_surf = font_desc.render(item["desc"], True, (150, 150, 150))
            surface.blit(name_surf, (item["rect"].x + 12, item["rect"].y + 10))
            surface.blit(desc_surf, (item["rect"].x + 12, item["rect"].y + 38))
            cost_x = item["rect"].right - 140
            cost_y = item["rect"].y + 15
            for mat, amount in item["cost"].items():
                player_amt = self.player.get_item_count(mat)
                mat_name = "Scrap" if mat == "frozen_scrap" else "Resin"
                sufficient = player_amt >= amount
                color = (255, 255, 255) if sufficient else (120, 120, 120)
                cost_text = f"{mat_name}: {player_amt}/{amount}"
                cost_surf = font_desc.render(cost_text, True, color)
                surface.blit(cost_surf, (cost_x, cost_y))
                cost_y += 18
        close_rect = pygame.Rect(container.x + 20, container.y + 375, 410, 45)
        hovered_close = close_rect.collidepoint(mx, my)
        close_bg = (60, 60, 60) if hovered_close else (30, 30, 30)
        pygame.draw.rect(surface, close_bg, close_rect, border_radius=6)
        pygame.draw.rect(surface, (255, 255, 255), close_rect, width=1, border_radius=6)
        font_btn = Fonts.Jersey_10(24)
        btn_text = font_btn.render("CLOSE [ESC]", True, (255, 255, 255))
        bx = close_rect.centerx - btn_text.get_width() // 2
        by = close_rect.centery - btn_text.get_height() // 2
        surface.blit(btn_text, (bx, by))

    def update(self):
        super().update()
        dt = self.get_game().get_dt()
        if self.state == "NORMAL" and self.player and self.player.has_item("ak47"):
            fire_weapon_at_mouse(self, dt)
        if hasattr(self, "furnace") and self.furnace:
            self.furnace.fuel = max(0.0, self.furnace.fuel - 2.5 * dt)
        for e in self.entities[:]:
            if isinstance(e, CollectibleItem):
                if self.player.rect.colliderect(e.rect):
                    self.player.add_item(e.item_type, 1)
                    self.remove_entity(e)

        if self.player.x < 15:
            self.player.transition_x = 900
            self.player.transition_y = 500
            self.remove_entity(self.player)
            self.game.set_scene("ingame.detachment")
            return
        elif self.player.x > 2005:
            self.player.transition_x = 100
            self.remove_entity(self.player)
            self.game.set_scene("ingame.guardedstorage")
            return

    def paint(self, surface: pygame.Surface):
        """
        Draw the game layer environment and active menu panels.
        :param surface: Target drawing pygame.Surface
        """
        super().paint(surface)
        if self.state == "CRAFTING":
            self.paint_crafting_ui(surface)
        else:
            self.paint_hud(surface)
        lines = [
            f"X: {int(self.player.x)} Y: {int(self.player.y)}",
            f"CamX: {int(self.tilemap.viewpoint.x)} CamY: {int(self.tilemap.viewpoint.y)}",
            f"HP: {int(self.player.health)}",
            f"Temp: {int(self.player.temperature)}",
            f"Scrap: {self.player.get_item_count('frozen_scrap')}",
            f"Resin: {self.player.get_item_count('alpine_resin')}",
            f"Coal: {self.player.get_item_count('coal')}",
            f"Furnace Fuel: {int(self.furnace.fuel)}",
            f"AK47: {self.player.has_item('ak47')}",
            f"Igniter: {self.player.has_item('igniter')}",
            f"Keychip: {self.player.has_item('keychip')}",
            f"Medkit: {self.player.get_item_count('medkit')}",
            f"Thermopack: {self.player.get_item_count('thermopack')}"
        ]
        paint_debug_lines(surface, lines)


class TailWorkshopScene(LayeredScene):

    def __init__(self):
        super().__init__()
        self.game_layer = TailWorkshopGameLayer()
        self.add_layer(self.game_layer)

    def on_enter(self):
        self.game_layer.on_enter()

    def reset(self):
        self.game_layer.reset()
