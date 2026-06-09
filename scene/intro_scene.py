import pygame

from scene import LayeredScene, WeightedBackgroundLayer, RepeatingImageLayer, TrainLayer


class IntroScene(LayeredScene):
    def __init__(self):
        super().__init__()

        self.stage1 = [
            WeightedBackgroundLayer(
                [
                    ("assets/images/background/intro/ruralparallaxriver.png", 8),
                    ("assets/images/background/intro/ruralparallaxriverfront.png", 8),
                    ("assets/images/background/intro/ruralparallaxriverskyredlex.png", 8),
                    ("assets/images/background/intro/ruralparallaxsky.png", 0),
                    ("assets/images/background/intro/ruralparallaxmountainback2.png", 0.2),
                    ("assets/images/background/intro/ruralparallaxmountainback.png", 1),
                    ("assets/images/background/intro/ruralparallaxmountain.png", 0.5),
                    ("assets/images/background/intro/ruralparallaxclouds.png", 8),
                    ("assets/images/background/intro/ruralparallaxvillage.png", 8),
                ]
            ),
            RepeatingImageLayer(
                ("assets/images/objects/rail.png", 2),
                0,
                offset_y=650,
                speed=8
            ),
            TrainLayer(
                [
                    "assets/images/objects/sub_engine.png",
                    "assets/images/objects/container.png",
                    "assets/images/objects/containers.png",
                    "assets/images/objects/prior_compartment.png",
                    "assets/images/objects/main_engine.png",
                ],
                scale=2,
                offset_y=636,
                offset_x=int(100),
            )
        ]

        self.add_layers(self.stage1)


    def paint(self, surface: pygame.Surface):
        super().paint(surface)
        self.stage1[0].tick()
        self.stage1[1].tick()

