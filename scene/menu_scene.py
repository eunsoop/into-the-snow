import pygame
from pygame import Surface, Rect

from core import LayeredScene, Layer, UserInterfaceLayer, Fonts
from ui import Button, Label

class MenuBackgroundLayer(Layer):

    def __init__(self):
        super().__init__()

        def scale_image(path):
            """
            Load and scale a background layer image to fit screen dimensions.
            :param path: Relative filesystem path to target background image asset
            :return: Scaled pygame.Surface image
            """
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

    def event(self, event):
        pass

    def paint(self, surface: Surface):
        """
        Scroll the middle background segment and draw other foreground layers.
        :param surface: Target drawing Surface
        """

        surface.blit(self.bg, (0, 0))
        
        if self.progress < -1:
            self.progress = 2
        self.progress -= self.get_game().get_dt() * 0.1
        
        surface.blit(self.target, (int(self.progress * self.target.get_width()), 0))
        
        for fg in self.fg:
            surface.blit(fg, (0, 0))

class MenuScene(LayeredScene):

    def __init__(self):
        super().__init__()
        self.show_settings = False
        self.show_credits = False
        self.bg_layer = MenuBackgroundLayer()
        self.ui_layer = UserInterfaceLayer(elements=[
            ((210, 50), 0, Label(
                text="Express - Into the snow",
                font=Fonts.JacquardaBastarda(54),
                color=(255, 255, 255)
            )),
            ((150, 200), 0, Button(
                (200, 50),
                Label("Play", Fonts.Jersey_10(32)),
                on_pressed=lambda: self.start_game(),
            )),
            ((150, 270), 0, Button(
                (200, 50),
                Label("Settings", Fonts.Jersey_10(32)),
                on_pressed=lambda: self.toggle_settings(),
            )),
            ((150, 340), 0, Button(
                (200, 50),
                Label("Credits", Fonts.Jersey_10(32)),
                on_pressed=lambda: self.toggle_credits(),
            )),
            ((150, 410), 0, Button(
                (200, 50),
                Label("Quit", Fonts.Jersey_10(32)),
                on_pressed=lambda: self.game.quit(),
            ))
        ])
        self.add_layer(self.bg_layer)
        self.add_layer(self.ui_layer)

    def start_game(self):
        self.game.reset_player_data()
        self.game.set_scene("intro")

    def toggle_settings(self):
        self.show_settings = not self.show_settings
        self.show_credits = False

    def toggle_credits(self):
        self.show_credits = not self.show_credits
        self.show_settings = False

    def paint(self, surface: Surface):
        super().paint(surface)
        
        if self.show_settings:
            panel_rect = Rect(450, 200, 400, 260)
            pygame.draw.rect(surface, (40, 40, 50), panel_rect)
            pygame.draw.rect(surface, (200, 200, 220), panel_rect, 2)
            font_title = Fonts.Jersey_10(28)
            font_text = Fonts.Jersey_10(20)
            surface.blit(font_title.render("Settings", True, (255, 255, 255)), (480, 220))
            surface.blit(font_text.render("- WASD: Move", True, (220, 220, 220)), (480, 270))
            surface.blit(font_text.render("- F Key: Interact", True, (220, 220, 220)), (480, 310))
            surface.blit(font_text.render("- Mouse Click: Shoot", True, (220, 220, 220)), (480, 350))
            surface.blit(font_text.render("- Goal: Fix the Engine", True, (220, 220, 255)), (480, 390))
            
        elif self.show_credits:
            panel_rect = Rect(450, 200, 400, 260)
            pygame.draw.rect(surface, (40, 40, 50), panel_rect)
            pygame.draw.rect(surface, (200, 200, 220), panel_rect, 2)
            font_title = Fonts.Jersey_10(28)
            font_text = Fonts.Jersey_10(20)
            surface.blit(font_title.render("Credits", True, (255, 255, 255)), (480, 220))
            surface.blit(font_text.render("Express - Into the snow", True, (240, 240, 250)), (480, 270))
            surface.blit(font_text.render("ICS3U Final Project", True, (220, 220, 220)), (480, 310))
            surface.blit(font_text.render("Made with Pygame", True, (220, 220, 220)), (480, 350))
            surface.blit(font_text.render("Thank you!", True, (200, 255, 200)), (480, 400))

