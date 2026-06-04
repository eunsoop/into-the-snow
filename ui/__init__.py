from abc import ABC, abstractmethod
from typing import final

import pygame
from pygame import Rect, Surface
from pygame._sdl2 import Image

from scene import Layer

def is_mouse_in_rect(mouse_pos: tuple[int, int], rect: tuple[int, int, int, int] | tuple) -> bool:
    return rect[0] <= mouse_pos[0] <= \
        rect[0] + rect[2] and rect[1] <= mouse_pos[1] <= rect[1] + rect[3]


class Element(ABC):
    def __init__(self):
        self.ui_layer = None


    @final
    def __set_ui_layer__(self, ui_layer): self.ui_layer = ui_layer
    @final
    def get_ui_layer(self): return self.ui_layer

    def event(self, event): pass
    @abstractmethod
    def update(self, surface: Surface, coordinate: tuple[int, int]): pass


class SizableElement(Element, ABC):
    def __init__(self, size: tuple[int, int], *args, **kwargs):
        super().__init__()
        self.size = size

    def get_size(self) -> tuple[int, int]:
        return self.size


class RichElementParameter:
    def __init__(self, color: tuple[int, int, int], background: Image | tuple[int, int, int] | None = None, radius: int = 0):
        self.color = color
        self.background = background
        self.radius = radius


class RichElement(SizableElement, ABC):
    def __init__(self, size: tuple[int, int], rich: RichElementParameter, *args, **kwargs):
        super().__init__(size, *args, **kwargs)
        self.rich = rich

    @property
    def rich_parameter(self):
        return self.rich


class UserInterfaceLayer(Layer):
    def __init__(self, elements: list[tuple[tuple[int, int], int, Element]] = []):
        """
        Initializes a new UserInterfaceLayer.

        :param elements: List of tuples (coordinate, z_index, element)
        """
        super().__init__()
        self.elements = elements

    def add_element(self, coordinate: tuple[int, int], element: Element, z_index: int = 0):
        self.elements.append((coordinate, z_index, element))
        element.__set_ui_layer__(self)

    def event(self, event):
        for element_data in sorted(self.elements, key=lambda e: e[1]):
            ele = element_data[2]
            if isinstance(ele, SizableElement):
                if not event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP: ele.event(event)
                if is_mouse_in_rect(pygame.mouse.get_pos(), (*element_data[0], *ele.size)): ele.event(event)
            else:
                ele.event(event)

    def paint(self, surface: Surface):
        for element_data in sorted(self.elements, key=lambda e: e[1]):
            ele = element_data[2]

            if isinstance(ele, SizableElement): surface.set_clip((*element_data[0], *ele.get_size()))
            ele.update(surface, element_data[0])
            surface.set_clip(None)