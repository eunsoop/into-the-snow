import pygame

cached_fonts: dict[tuple[str, int], pygame.font.Font] = {}

class Fonts:
    @classmethod
    def __get_font__(cls, font_name: str, size: int) -> pygame.font.Font:
        """
        Load and cache a font from the filesystem if not already cached.
        :param cls: The Fonts class context
        :param font_name: Path to the TrueType Font (.ttf) file
        :param size: Height of font characters in pixels
        :return: Cached pygame.font.Font object instance
        """
        if (font_name, size) not in cached_fonts:
            cached_fonts[(font_name, size)] = pygame.font.Font(font_name, size)
        return cached_fonts[(font_name, size)]

    @classmethod
    def Jersey_10(cls, size: int = 16) -> pygame.font.Font:
        """
        Retrieve a cached instance of the 'Jersey 10' font style.
        :param cls: The Fonts class context
        :param size: Pixel size of the font
        :return: Cached pygame.font.Font instance
        """
        return Fonts.__get_font__("assets/fonts/Jersey_10/Jersey10-Regular.ttf", size)

    @classmethod
    def JacquardaBastarda(cls, size: int = 16) -> pygame.font.Font:
        """
        Retrieve a cached instance of the 'Jacquarda Bastarda 9' font style.
        :param cls: The Fonts class context
        :param size: Pixel size of the font
        :return: Cached pygame.font.Font instance
        """
        return Fonts.__get_font__("assets/fonts/Jacquarda_Bastarda_9/JacquardaBastarda9-Regular.ttf", size)

