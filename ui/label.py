import pygame
from pygame import Surface, sysfont
from pygame.ftfont import Font

from core import Element

if not pygame.sysfont.is_init:
    pygame.font.init()


class Label(Element):
    def __init__(self, text: str, font: Font = sysfont.SysFont("Arial", size=16), color: tuple[int, int, int] = (255, 255, 255), antialias: bool = True, background: tuple[int, int, int] | None = None):
        super().__init__()
        self.text = text
        self.font = font
        self.color = color
        self.antialias = antialias
        self.background = background

    def get_rendered_size(self) -> tuple[int, int]:
        return self.font.size(self.text)

    def update(self, surface: Surface, coordinate: tuple[int, int]):
        surface.blit(self.font.render(self.text, self.antialias, self.color, self.background), coordinate)