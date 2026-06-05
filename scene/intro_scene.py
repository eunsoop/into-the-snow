from pygame import Surface

from scene import LayeredScene, WeightedBackgroundLayer


class IntroScene(LayeredScene):
    def __init__(self):
        super().__init__()

        self.stage1 = WeightedBackgroundLayer(
            [
                ("assets/images/background/intro/ruralparallaxriver.png", 10),
                ("assets/images/background/intro/ruralparallaxriverfront.png", 10),
                ("assets/images/background/intro/ruralparallaxriverskyredlex.png", 10),
                ("assets/images/background/intro/ruralparallaxsky.png", 0),
                ("assets/images/background/intro/ruralparallaxmountainback2.png", 0.2),
                ("assets/images/background/intro/ruralparallaxmountainback.png", 0.4),
                ("assets/images/background/intro/ruralparallaxmountain.png", 0.5),
                ("assets/images/background/intro/ruralparallaxclouds.png", 10),
                ("assets/images/background/intro/ruralparallaxvillage.png", 10),
            ]
        )

        self.add_layer(self.stage1)

    def paint(self, surface: Surface):
        self.stage1.paint(surface)
        self.stage1.tick()