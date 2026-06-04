from pygame import Surface, sysfont
from pygame.ftfont import Font

from ui import Element


class Label(Element):
    def __init__(self, text: str, font: Font = sysfont.SysFont("Arial", size=16), *args, **kwargs):
        super().__init__(
            *args, **kwargs
        )
        self.text = text
        self.font = font

    def get_rendered_size(self) -> tuple[int, int]:
        return self.font.size(self.text)

    def update(self, surface: Surface, coordinate: tuple[int, int]):
        self.font.render_to(surface, coordinate, self.text)