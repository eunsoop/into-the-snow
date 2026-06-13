import pygame
from pygame import Surface, sysfont
from pygame.ftfont import Font

from core import Element

if not pygame.sysfont.is_init:
    pygame.font.init()

class Label(Element):

    def __init__(
        self,
        text: str,
        font: Font = sysfont.SysFont("Arial", size=16),
        color: tuple[int, int, int] = (255, 255, 255),
        antialias: bool = True,
        background: tuple[int, int, int] | None = None,
    ):
        """
        Initialize the Label.
        :param text: String contents to display
        :param font: pygame Font object used for rendering (defaults to Arial 16)
        :param color: RGB text color (default white)
        :param antialias: Set True to apply text smoothing
        :param background: Optional RGB background color behind characters
        """
        super().__init__()
        self.text = text
        self.font = font
        self.color = color
        self.antialias = antialias
        self.background = background

    def get_rendered_size(self) -> tuple[int, int]:
        """
        Calculate the width and height of the rendered label text surface.
        :return: Tuple (width, height) of pixel dimensions
        """
        return self.font.size(self.text)

    def update(self, surface: Surface, coordinate: tuple[int, int]):
        surface.blit(self.font.render(self.text, self.antialias, self.color, self.background), coordinate)