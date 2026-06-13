from abc import ABC, abstractmethod
from typing import final

import pygame
from pygame import Surface
from pygame._sdl2 import Image

from core.layer import Layer

def is_mouse_in_rect(mouse_pos: tuple[int, int], rect: tuple[int, int, int, int]) -> bool:
    """
    Check if the mouse pointer coordinates are within a boundary rectangle.
    :param mouse_pos: Tuple (x, y) containing the mouse coordinate
    :param rect: Tuple (x, y, width, height) of the rectangle region
    :return: True if the mouse is inside the rectangle boundary, False otherwise
    """
    return rect[0] <= mouse_pos[0] <= rect[0] + rect[2] and rect[1] <= mouse_pos[1] <= rect[1] + rect[3]

class Element(ABC):
    def __init__(self):
        self.ui_layer = None

    @final
    def __set_ui_layer__(self, ui_layer):
        self.ui_layer = ui_layer

    @final
    def get_ui_layer(self):
        """
        Retrieve the UI layer that owns this element.
        :return: Parent UserInterfaceLayer instance
        """
        return self.ui_layer

    def event(self, event: pygame.event.Event):
        pass

    @abstractmethod
    def update(self, surface: Surface, coordinate: tuple[int, int]):
        pass

class SizableElement(Element, ABC):
    def __init__(self, size: tuple[int, int], *args, **kwargs):
        super().__init__()
        self.size = size

    def get_size(self) -> tuple[int, int]:
        """
        Get the dimensions of the sizable element.
        :return: Tuple (width, height) specifying size
        """
        return self.size

class RichElementParameter:
    def __init__(self, color: tuple[int, int, int], background: Image | tuple[int, int, int] | None = None, radius: int = 0):
        """
        Initialize the rich element style parameter constraints.
        :param color: RGB tuple for borders/text color
        :param background: Optional Surface image or RGB tuple for fills
        :param radius: Border corner radius for rectangles
        """
        self.color = color
        self.background = background
        self.radius = radius

class RichElement(SizableElement, ABC):
    def __init__(self, size: tuple[int, int], rich: RichElementParameter, *args, **kwargs):
        super().__init__(size, *args, **kwargs)
        self.rich = rich

    @property
    def rich_parameter(self) -> RichElementParameter:
        """
        Retrieve style parameters associated with the rich element.
        :return: RichElementParameter style options
        """
        return self.rich

class UserInterfaceLayer(Layer):
    def __init__(self, elements=None):
        super().__init__()
        self.elements = elements if elements is not None else []

    def add_element(self, coordinate: tuple[int, int], element: Element, z_index: int = 0):
        self.elements.append((coordinate, z_index, element))
        element.__set_ui_layer__(self)

    def event(self, event: pygame.event.Event):
        for element_data in sorted(self.elements, key=lambda e: e[1]):
            ele = element_data[2]
            if isinstance(ele, SizableElement):

                if not event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
                    ele.event(event)
                if is_mouse_in_rect(pygame.mouse.get_pos(), (*element_data[0], *ele.size)):
                    ele.event(event)
            else:
                ele.event(event)

    def paint(self, surface: Surface):
        for element_data in sorted(self.elements, key=lambda e: e[1]):
            ele = element_data[2]
            if isinstance(ele, SizableElement):

                surface.set_clip((*element_data[0], *ele.get_size()))
            ele.update(surface, element_data[0])
            surface.set_clip(None)

