import pygame

from core import LayeredScene, Fonts
from scene.background_layers import WeightedBackgroundLayer, RepeatingImageLayer, TrainLayer


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
                offset_x=100,
            )
        ]
        self.add_layers(self.stage1)

    def event(self, event):
        super().event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.game.set_scene("ingame.tailworkshop")

    def paint(self, surface: pygame.Surface):
        super().paint(surface)
        self.stage1[0].tick()
        self.stage1[1].tick()

        overlay = pygame.Rect(100, 100, 800, 360)
        overlay_surf = pygame.Surface((800, 360), pygame.SRCALPHA)
        overlay_surf.fill((30, 30, 40, 220))
        surface.blit(overlay_surf, (100, 100))
        pygame.draw.rect(surface, (255, 255, 255), overlay, 2)

        font_title = Fonts.Jersey_10(32)
        font_text = Fonts.Jersey_10(20)

        surface.blit(font_title.render("EXPRESS - INTO THE SNOW", True, (255, 255, 255)), (130, 120))

        story_lines = [
            "You are on a fast train in a freezing storm.",
            "Goal: go to subengine and fix it.",
            "1. Workshop: get scrap & resin",
            "2. Storage: steal igniter & keychip.",
            "3. Workbench: make gun",
            "4. Furnace: stay warm",
            "5. Engine: fix the subengine",
            "   [Press SPACE to Start]"
        ]
        y = 170
        for line in story_lines:
            color = (150, 255, 150) if "SPACE" in line else (220, 220, 220)
            surface.blit(font_text.render(line, True, color), (130, y))
            y += 30
