import random

import pygame


class Effector:
    def update(self, dt: float):
        pass

    def apply_offset(self) -> tuple[float, float]:
        """
        Calculate and return the current camera position offset.
        :return: Tuple (offset_x, offset_y)
        """
        return 0.0, 0.0

    def apply_post(self, surface: pygame.Surface):
        pass

    def is_finished(self) -> bool:
        """
        Check if the effector duration has expired.
        :return: True if finished, False otherwise
        """
        return False


class ShakeEffector(Effector):
    def __init__(self, duration: float, intensity: float, start_duration: float = 0):
        """
        Initialize a camera shake effector with specific duration and intensity.
        :param duration: Time in seconds the shake effect lasts
        :param intensity: Maximum pixel offset displacement range
        """
        self.duration = duration
        self.intensity = intensity
        self.elapsed = -start_duration

    def update(self, dt: float):
        self.elapsed += dt

    def apply_offset(self) -> tuple[float, float]:
        """
        Generate random camera offset values based on current shake decay intensity.
        :return: Tuple (offset_x, offset_y) in pixels
        """
        if self.is_finished() or self.elapsed < 0:
            return 0.0, 0.0

        ratio = 1.0 - (self.elapsed / self.duration)
        current_intensity = self.intensity * ratio
        dx = random.uniform(-current_intensity, current_intensity)
        dy = random.uniform(-current_intensity, current_intensity)
        return dx, dy

    def is_finished(self) -> bool:
        """
        Check if shake duration has elapsed.
        :return: True if duration is reached, False otherwise
        """
        return self.elapsed >= self.duration


class FlashEffector(Effector):
    def __init__(self, duration: float, color: tuple[int, int, int], max_alpha: int = 100):
        """
        Initialize screen flash effector.
        :param duration: Time in seconds the flash takes to fade out
        :param color: RGB color tuple of the flash overlay
        :param max_alpha: Initial transparency alpha value (0-255)
        """
        self.duration = duration
        self.color = color
        self.max_alpha = max_alpha
        self.elapsed = 0.0

    def update(self, dt: float):
        self.elapsed += dt

    def apply_post(self, surface: pygame.Surface):
        """
        Render the fading semi-transparent color overlay onto the scene surface.
        :param surface: The destination drawing pygame.Surface
        """
        if self.is_finished():
            return

        ratio = 1.0 - (self.elapsed / self.duration)
        alpha = int(self.max_alpha * ratio)
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((*self.color, alpha))
        surface.blit(overlay, (0, 0))

    def is_finished(self) -> bool:
        """
        Check if flash fade duration has finished.
        :return: True if fully faded out, False otherwise
        """
        return self.elapsed >= self.duration


class TrainShakeEffector(Effector):
    def __init__(self, base_intensity: float = 0.5, jolt_frequency: float = 4.0,
                 jolt_intensity: float = 2.0, jolt_duration: float = 0.4):
        """
        Initialize periodic train rumble effector.
        :param base_intensity: Constant background vibration intensity
        :param jolt_frequency: Average delay interval in seconds between large jolts
        :param jolt_intensity: Magnitude of periodic train jolts
        :param jolt_duration: Time in seconds that a jolt lasts
        """
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
        """
        Calculate train rumble offset including periodic high-intensity jolts.
        :return: Tuple (offset_x, offset_y) in pixels
        """
        intensity = self.base_intensity
        if self.is_jolting:
            ratio = 1.0 - (self.current_jolt_elapsed / self.jolt_duration)
            intensity += self.jolt_intensity * ratio
        dx = random.uniform(-intensity, intensity)
        dy = random.uniform(-intensity, intensity)
        return dx, dy

    def is_finished(self) -> bool:
        """
        Train shake effect is persistent and never finishes automatically.
        :return: Always False
        """
        return False
