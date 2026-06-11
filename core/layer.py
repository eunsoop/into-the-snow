import pygame
import random
from abc import abstractmethod, ABC
from typing import final
from pygame import Surface


class Effector:
    def update(self, dt: float):
        pass

    def apply_offset(self) -> tuple[float, float]:
        return (0.0, 0.0)

    def apply_post(self, surface: pygame.Surface):
        pass

    def is_finished(self) -> bool:
        return False


class ShakeEffector(Effector):
    def __init__(self, duration: float, intensity: float):
        self.duration = duration
        self.intensity = intensity
        self.elapsed = 0.0

    def update(self, dt: float):
        self.elapsed += dt

    def apply_offset(self) -> tuple[float, float]:
        if self.is_finished():
            return (0.0, 0.0)
        ratio = 1.0 - (self.elapsed / self.duration)
        current_intensity = self.intensity * ratio
        dx = random.uniform(-current_intensity, current_intensity)
        dy = random.uniform(-current_intensity, current_intensity)
        return (dx, dy)

    def is_finished(self) -> bool:
        return self.elapsed >= self.duration


class FlashEffector(Effector):
    def __init__(self, duration: float, color: tuple[int, int, int], max_alpha: int = 100):
        self.duration = duration
        self.color = color
        self.max_alpha = max_alpha
        self.elapsed = 0.0

    def update(self, dt: float):
        self.elapsed += dt

    def apply_post(self, surface: pygame.Surface):
        if self.is_finished():
            return
        ratio = 1.0 - (self.elapsed / self.duration)
        alpha = int(self.max_alpha * ratio)
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((*self.color, alpha))
        surface.blit(overlay, (0, 0))

    def is_finished(self) -> bool:
        return self.elapsed >= self.duration


class TrainShakeEffector(Effector):
    def __init__(self, base_intensity: float = 0.5, jolt_frequency: float = 4.0, jolt_intensity: float = 2.0, jolt_duration: float = 0.4):
        self.base_intensity = base_intensity
        self.jolt_frequency = jolt_frequency
        self.jolt_intensity = jolt_intensity
        self.jolt_duration = jolt_duration
        self.jolt_timer = random.uniform(0.0, jolt_frequency)
        self.current_jolt_elapsed = 0.0
        self.is_jolting = False

    def update(self, dt: float):
        if self.is_jolting:
            self.current_jolt_elapsed += dt
            if self.current_jolt_elapsed >= self.jolt_duration:
                self.is_jolting = False
                self.current_jolt_elapsed = 0.0
                self.jolt_timer = 0.0
        else:
            self.jolt_timer += dt
            if self.jolt_timer >= self.jolt_frequency:
                self.is_jolting = True
                self.current_jolt_elapsed = 0.0

    def apply_offset(self) -> tuple[float, float]:
        intensity = self.base_intensity
        if self.is_jolting:
            ratio = 1.0 - (self.current_jolt_elapsed / self.jolt_duration)
            intensity += self.jolt_intensity * ratio
        
        dx = random.uniform(-intensity, intensity)
        dy = random.uniform(-intensity, intensity)
        return (dx, dy)

    def is_finished(self) -> bool:
        return False


class Layer(ABC):
    def __init__(self):
        self.game = None
        self.surface = None
        self.effectors = []

    def add_effector(self, effector: Effector):
        self.effectors.append(effector)

    @final
    def __set_game__(self, game):
        self.game = game
        self.surface = Surface(game.get_surface().get_size(), pygame.SRCALPHA) if game is not None else None

    @final
    def get_game(self):
        return self.game

    @abstractmethod
    def event(self, event: pygame.event.Event):
        pass

    @abstractmethod
    def paint(self, surface: Surface):
        pass

    def reset(self):
        pass


class GameLayer(Layer):
    def __init__(self):
        super().__init__()
        self.entities = []

    def add_entity(self, entity):
        self.entities.append(entity)
        entity.layer = self

    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)
            entity.layer = None

    def event(self, event: pygame.event.Event):
        for e in self.entities:
            e.event(event)

    def update(self):
        pass

    def paint(self, surface: Surface):
        self.update()
        for e in self.entities:
            e.update()

        if hasattr(self, 'tilemap') and self.tilemap:
            player = getattr(self, 'player', None)
            if player:
                width, height = surface.get_width(), surface.get_height()
                view_x = width / 2 - player.x
                view_y = height / 2 - player.y

                ts = self.tilemap.tile.tile_size * self.tilemap.viewpoint.z
                map_width = len(self.tilemap.map_data[next(iter(self.tilemap.map_data))]) * ts if self.tilemap.map_data else 0
                map_height = len(self.tilemap.map_data) * ts

                min_x = width - map_width
                min_y = height - map_height

                if min_x > 0:
                    view_x = min_x / 2
                else:
                    view_x = max(min_x, min(0, view_x))

                if min_y > 0:
                    view_y = min_y / 2
                else:
                    view_y = max(min_y, min(0, view_y))

                self.tilemap.viewpoint.x = view_x
                self.tilemap.viewpoint.y = view_y

            self.tilemap.paint(surface)

        viewpoint = getattr(self.tilemap, 'viewpoint', None) if hasattr(self, 'tilemap') and self.tilemap else None
        for e in sorted(self.entities, key=lambda e: e.z_index):
            if viewpoint:
                orig_center = e.rect.center
                e.rect.x += viewpoint.x
                e.rect.y += viewpoint.y
                e.paint(surface)
                e.rect.center = orig_center
            else:
                e.paint(surface)
