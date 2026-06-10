from typing import Callable
import pygame
from pygame import Surface

from core import RichElement, RichElementParameter
from ui.label import Label


class Button(RichElement):
    def __init__(
        self,
        size: tuple[int, int],
        label: Label | None = None,
        rich: RichElementParameter = RichElementParameter((255, 255, 255), (0, 0, 0), 0),
        disabled: bool = False,
        on_pressed: Callable | None = None,
    ):
        super().__init__(size, rich)
        self.label = label
        self.disabled = disabled
        self.on_pressed = on_pressed

    def update(self, surface: Surface, coordinate: tuple[int, int]):
        if isinstance(self.rich_parameter.background, pygame.Surface):
            surface.blit(self.rich_parameter.background, dest=(*coordinate, *self.get_size()))
        if isinstance(self.rich_parameter.background, tuple):
            pygame.draw.rect(surface, self.rich_parameter.background, (*coordinate, *self.get_size()), self.rich_parameter.radius)

        if self.label:
            size = self.label.get_rendered_size()
            self.label.update(surface, (coordinate[0] + self.size[0] // 2 - size[0] // 2, coordinate[1] + self.size[1] // 2 - size[1] // 2))
        if self.disabled:
            pygame.draw.rect(surface, (128, 128, 128), (*coordinate, *self.get_size()), self.rich_parameter.radius)

    def event(self, event: pygame.event.Event):
        if self.disabled or self.on_pressed is None:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
            self.on_pressed()