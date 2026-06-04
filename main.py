from asyncio import Event

import pygame

from scene import Scene
from scene.drawing_scene import DrawingScene

WIDTH, HEIGHT = 800, 600

class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.is_running = True

        self.scenes = {}
        self.current_scene = None


    def register_scene(self, id: str, scene: Scene):
        self.scenes[id] = scene
        scene.__set_game__(self)


    def set_scene(self, id: str):
        self.current_scene = self.scenes[id]


    def event(self, event):
        self.current_scene.event(event)


    def loop(self):
        self.surface.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.quit()
            self.event(event)

        self.current_scene.paint()
        pygame.display.flip()


    def quit(self):
        self.is_running = False
        pygame.quit()


    def run(self):
        while self.is_running: self.loop()


if __name__ == "__main__":
    game = Game()
    game.register_scene("drawing", DrawingScene())
    game.set_scene("drawing")
    game.run()
