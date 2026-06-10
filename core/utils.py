import pygame

cached_fonts: dict[tuple[str, int], pygame.font.Font] = {}


class Fonts:
    @classmethod
    def __get_font__(cls, font_name: str, size: int) -> pygame.font.Font:
        if not (font_name, size) in cached_fonts:
            cached_fonts[(font_name, size)] = pygame.font.Font(font_name, size)
        return cached_fonts[(font_name, size)]

    @classmethod
    def Jersey_10(cls, size: int = 16) -> pygame.font.Font:
        return Fonts.__get_font__("assets/fonts/Jersey_10/Jersey10-Regular.ttf", size)

    @classmethod
    def JacquardaBastarda(cls, size: int = 16) -> pygame.font.Font:
        return Fonts.__get_font__("assets/fonts/Jacquarda_Bastarda_9/JacquardaBastarda9-Regular.ttf", size)


class Sprite:
    def __init__(self, x: float, y: float, image: pygame.Surface):
        self.x = x
        self.y = y
        self.image = image
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self):
        self.rect.center = (int(self.x), int(self.y))

    def paint(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)


def is_mouse_in_rect(mouse_pos: tuple[int, int], rect: tuple[int, int, int, int] | tuple) -> bool:
    return rect[0] <= mouse_pos[0] <= rect[0] + rect[2] and rect[1] <= mouse_pos[1] <= rect[1] + rect[3]
