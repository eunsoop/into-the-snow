import pygame

from scene import Scene
from scene.menu_scene import MenuScene

WIDTH, HEIGHT = 1000, 700

class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.is_running = True
        self.clock = pygame.time.Clock()
        self.dt = 0

        self.scenes = {}
        self.current_scene = None

    def get_dt(self): return self.dt


    def register_scene(self, scene_id: str, scene: Scene):
        self.scenes[scene_id] = scene
        scene.__set_game__(self)


    def set_scene(self, scene_id: str):
        self.current_scene = self.scenes[scene_id]


    def event(self, event):
        self.current_scene.event(event)


    def loop(self):
        self.dt = self.clock.tick(60) / 1000.0

        self.surface.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.quit()
            self.event(event)

        self.current_scene.paint(self.surface)
        pygame.display.flip()


    def quit(self):
        self.is_running = False
        pygame.quit()


    def run(self):
        while self.is_running: self.loop()


if __name__ == "__main__":
    game = Game()
    game.register_scene("menu", MenuScene())
    game.set_scene("menu")
    game.run()
