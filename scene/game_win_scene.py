import pygame

from core import LayeredScene, UserInterfaceLayer, Fonts
from ui import Button, Label


class GameWinScene(LayeredScene):
    def __init__(self):
        super().__init__()
        
        self.ui_layer = UserInterfaceLayer(elements=[
            ((220, 180), 0, Label(
                text="CORE INSTALLED",
                font=Fonts.Jersey_10(48),
                color=(50, 255, 50)
            )),
            ((310, 250), 0, Label(
                text="GG",
                font=Fonts.Jersey_10(24),
                color=(200, 250, 200)
            )),
            ((425, 360), 0, Button(
                size=(150, 50),
                label=Label("Main Menu", Fonts.Jersey_10(28)),
                on_pressed=lambda: self.game.set_scene("menu")
            ))
        ])
        self.add_layer(self.ui_layer)

    def paint(self, surface: pygame.Surface):
        surface.fill((10, 30, 15))
        super().paint(surface)
