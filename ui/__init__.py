from abc import ABC, abstractmethod
from typing import final

from pygame import Rect, Surface
from pygame._sdl2 import Image

from scene import Layer


class Element(ABC):
    def __init__(self, coordinate: tuple[int, int], z_index: int = 0):
        self.coordinate = coordinate
        self.z_index = z_index
        self.ui_layer = None


    @final
    def __set_ui_layer__(self, ui_layer): self.ui_layer = ui_layer
    @final
    def get_ui_layer(self): return self.ui_layer

    def event(self, event): pass
    @abstractmethod
    def update(self, surface: Surface, coordinate: tuple[int, int]): pass


class SizableElement(Element, ABC):
    def __init__(self, rect: Rect, z_index: int = 0):
        super().__init__(rect.topleft, z_index)
        self.rect = rect

    @property
    def coordinate(self) -> tuple[int, int]:
        return self.rect.topleft


class RichElementParameter:
    def __init__(self, color: tuple[int, int, int], background: Image | tuple[int, int, int] | None = None, radius: int = 0):
        self.color = color
        self.background = background
        self.radius = radius


class RichElement(SizableElement, ABC):
    def __init__(self, rich: RichElementParameter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rich = rich

    @property
    def rich_parameter(self):
        return self.rich


class UserInterfaceLayer(Layer):
    def __init__(self):
        super().__init__()
        self.elements = []

    def add_element(self, element: Element):
        self.elements.append(element)

    def event(self, event):
        for element in self.elements:
            element.event(event)

    def paint(self, surface: Surface):
        for element in sorted(self.elements, key=lambda e: e.z_index):
            if isinstance(element, SizableElement): surface.set_clip(element.rect)
            element.update(surface, element.coordinate)
            surface.set_clip(None)