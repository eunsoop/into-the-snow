import pygame

from core import LayeredScene, UserInterfaceLayer, Fonts
from ui import Button, Label


class GameOverScene(LayeredScene):
    def __init__(self):
        super().__init__()
        self.ui_layer = UserInterfaceLayer(elements=[
            ((280, 180), 0, Label(
                text="YOU FROZE",
                font=Fonts.Jersey_10(48),
                color=(255, 50, 50)
            )),
            ((300, 250), 0, Label(
                text="You froze in the storm.",
                font=Fonts.Jersey_10(24),
                color=(200, 200, 200)
            )),
            ((425, 360), 0, Button(
                size=(150, 50),
                label=Label("Main Menu", Fonts.Jersey_10(28)),
                on_pressed=lambda: self.game.set_scene("menu")
            ))
        ])
        self.add_layer(self.ui_layer)

    def paint(self, surface: pygame.Surface):
        surface.fill((30, 10, 10))
        super().paint(surface)
