import pygame
from pygame import Surface, Rect

from scene import LayeredScene, Layer
from ui import UserInterfaceLayer
from ui.button import Button
from ui.label import Label
from utils import Fonts


class MenuBackgroundLayer(Layer):
    def __init__(self):
        super().__init__()
        
        def scale_image(path):
            img = pygame.image.load(path)
            scale = max(1000 / img.get_width(), 700 / img.get_height())
            return pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        
        self.bg = scale_image("assets/images/background/menu/Plan 5.png")
        self.target = scale_image("assets/images/background/menu/Plan 4.png")
        self.fg = [
            scale_image("assets/images/background/menu/Plan 3.png"),
            scale_image("assets/images/background/menu/Plan 2.png"),
            scale_image("assets/images/background/menu/Plan 1.png"),
        ]

        self.progress = 1

    def event(self, event): pass

    def paint(self, surface: Surface):
        surface.blit(self.bg, (0, 0))

        if self.progress < -1: self.progress = 2
        self.progress -= self.get_game().get_dt()*0.1
        surface.blit(self.target, (int(self.progress * self.target.get_width()), 0))

        for fg in self.fg: surface.blit(fg, (0, 0))


class MenuScene(LayeredScene):
    def __init__(self):
        super().__init__(
            layers=[
                MenuBackgroundLayer(),
                UserInterfaceLayer(elements=[
                    ((210,50), 0, Label(
                        text="Into The Snow",
                        font=Fonts.JacquardaBastarda(48),
                        color=(255,255,255)
                    )),
                    ((315, 200), 0, Button(
                        (150, 50),
                        Label(
                            "Play",
                            Fonts.Jersey_10(32)
                        ),
                        on_pressed = lambda: self.game.set_scene("progress_selector"),
                    )),
                    ((315, 280), 0, Button(
                        (150, 50),
                        Label(
                            "Settings",
                            Fonts.Jersey_10(32)
                        ),
                        on_pressed = lambda: self.game.set_scene("settings"),
                    ))
                    ,
                    ((315, 360), 0, Button(
                        (150, 50),
                        Label(
                            "Credit",
                            Fonts.Jersey_10(32)
                        ),
                        on_pressed = lambda: self.game.set_scene("credit"),
                    ))
                ])
            ]
        )

