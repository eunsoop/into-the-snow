from typing import Callable

import pygame
from pygame import Surface

from ui import RichElement
from ui.label import Label


class Button(RichElement):
    def __init__(
        self,
        label: Label | None = None,
        disabled: bool = False,
        on_pressed: Callable | None = None,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.label = label
        self.disabled = disabled
        self.on_pressed = on_pressed


    def update(self, surface: Surface, coordinate: tuple[int, int]):
        if isinstance(self.rich_parameter.background, pygame.Surface): surface.blit(self.rich_parameter.background, dest=self.rect)
        if isinstance(self.rich_parameter.background, tuple): pygame.draw.rect(surface, self.rich_parameter.background, self.rect, self.rich_parameter.radius)

        if self.label: self.label.update(surface, coordinate)
        if self.disabled: pygame.draw.rect(surface, (128, 128, 128), self.rect, self.rich_parameter.radius)


    def event(self, event):
        if self.disabled or self.on_pressed is None: return
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and pygame.mouse.get_pos() in self.rect:
            self.on_pressed()