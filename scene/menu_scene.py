from pygame import Surface

from scene import LayeredScene, Layer


class MenuBackgroundLayer(Layer):
    def event(self, event):
        pass

    def paint(self, surface: Surface):
        pass


class MenuScene(LayeredScene):
    def __init__(self):
        super().__init__(
            layers=[

            ]
        )

