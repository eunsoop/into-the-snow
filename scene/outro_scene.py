import pygame

from core import LayeredScene, Layer, Fonts
from scene.background_layers import WeightedBackgroundLayer, RepeatingImageLayer

class DetachingTrainLayer(Layer):
    def __init__(self, scale: float = 2, offset_x: int = 100, offset_y: int = 636):
        super().__init__()
        
        def scale_image(path):
            img = pygame.image.load(path)
            return pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))

        self.sub_engine_img = scale_image("assets/images/objects/sub_engine.png")
        
        self.rest_imgs = [
            scale_image("assets/images/objects/container.png"),
            scale_image("assets/images/objects/containers.png"),
            scale_image("assets/images/objects/prior_compartment.png"),
            scale_image("assets/images/objects/main_engine.png"),
        ]
        
        self.max_height = max(
            self.sub_engine_img.get_height(),
            max(img.get_height() for img in self.rest_imgs)
        )
        self.offset_x = offset_x
        self.offset_y = offset_y
        
        self.separation_distance = 0.0
        self.timer = 0.0

    def event(self, event: pygame.event.Event):
        pass

    def paint(self, surface: pygame.Surface):
        if self.game:
            dt = self.game.get_dt()
            self.timer += dt
            if self.timer > 1.0:
                self.separation_distance += 150.0 * dt

        sub_x = self.offset_x - self.separation_distance
        sub_y = self.offset_y + self.max_height - self.sub_engine_img.get_height()
        surface.blit(self.sub_engine_img, (sub_x, sub_y))
        
        off = self.offset_x + self.sub_engine_img.get_width()
        for img in self.rest_imgs:
            y = self.offset_y + self.max_height - img.get_height()
            surface.blit(img, (off, y))
            off += img.get_width()

class OutroScene(LayeredScene):
    def __init__(self):
        super().__init__()
        self.train_layer = DetachingTrainLayer(scale=2, offset_y=636, offset_x=100)
        self.stage1 = [
            WeightedBackgroundLayer(
                [
                    (f"assets/images/background/detach/{i}.png", 0.4*(5-i)) for i in range(5, 1, -1)
                ],
                -40
            ),
            RepeatingImageLayer(
                ("assets/images/objects/rail.png", 2),
                0,
                offset_y=650,
                speed=8
            ),
            self.train_layer
        ]
        self.add_layers(self.stage1)
        self.timer = 0.0

    def paint(self, surface: pygame.Surface):
        dt = self.game.get_dt()
        self.timer += dt
        if self.timer > 6.0:
            self.game.set_scene("gamewin")
        super().paint(surface)
        self.stage1[0].tick()
        self.stage1[1].tick()
        
        if self.timer > 1.0:
            font_title = Fonts.Jersey_10(32)
            text_surf = font_title.render("SUB-ENGINE DECOUPLED", True, (255, 255, 255))
            
            overlay_surf = pygame.Surface((surface.get_width(), 60), pygame.SRCALPHA)
            overlay_surf.fill((0, 0, 0, 150))
            surface.blit(overlay_surf, (0, 100))
            surface.blit(text_surf, (surface.get_width() // 2 - text_surf.get_width() // 2, 115))

    def reset(self):
        self.timer = 0.0
        self.train_layer.timer = 0.0
        self.train_layer.separation_distance = 0.0
