import random

import pygame


class Effector:
    def update(self, dt: float):
        pass

    def apply_offset(self) -> tuple[float, float]:
        return 0.0, 0.0

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
            return 0.0, 0.0
        ratio = 1.0 - (self.elapsed / self.duration)
        current_intensity = self.intensity * ratio
        dx = random.uniform(-current_intensity, current_intensity)
        dy = random.uniform(-current_intensity, current_intensity)
        return dx, dy

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
    def __init__(self, base_intensity: float = 0.5, jolt_frequency: float = 4.0,
                 jolt_intensity: float = 2.0, jolt_duration: float = 0.4):
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
        return dx, dy

    def is_finished(self) -> bool:
        return False
