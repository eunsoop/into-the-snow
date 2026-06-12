import pygame

from core import Scene
from entity.player import Player
from scene.intro_scene import IntroScene
from scene.menu_scene import MenuScene
from scene.tail_workshop_scene import TailWorkshopScene
from scene.guarded_storage_scene import GuardedStorageScene
from scene.engine_room_scene import EngineRoomScene
from scene.game_over_scene import GameOverScene
from scene.game_win_scene import GameWinScene
from scene.detachment_scene import DetachmentScene
from scene.outro_scene import OutroScene

WIDTH, HEIGHT = 1000, 700


class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.is_running = True
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.scenes = {}
        self.current_scene = None
        self.player = Player(150, 300)

    def reset_player_data(self):
        self.player = Player(150, 300)
        for scene in self.scenes.values():
            if hasattr(scene, "reset"):
                scene.reset()

    def get_dt(self) -> float:
        return self.dt

    def get_surface(self) -> pygame.Surface:
        return self.surface

    def register_scene(self, scene_id: str, scene: Scene):
        self.scenes[scene_id] = scene
        scene.__set_game__(self)

    def set_scene(self, scene_id: str):
        self.current_scene = self.scenes[scene_id]
        if hasattr(self.current_scene, "on_enter"):
            self.current_scene.on_enter()

    def event(self, event: pygame.event.Event):
        if self.current_scene:
            self.current_scene.event(event)

    def loop(self):
        self.dt = self.clock.tick(60) / 1000.0
        self.surface.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            self.event(event)
        if self.current_scene:
            self.current_scene.paint(self.surface)
        pygame.display.flip()

    def quit(self):
        self.is_running = False
        pygame.quit()

    def run(self):
        while self.is_running:
            self.loop()


if __name__ == "__main__":
    game = Game()
    game.register_scene("menu", MenuScene())
    game.register_scene("intro", IntroScene())
    game.register_scene("ingame.engineroom", EngineRoomScene())
    game.register_scene("ingame.tailworkshop", TailWorkshopScene())
    game.register_scene("ingame.guardedstorage", GuardedStorageScene())
    game.register_scene("ingame.detachment", DetachmentScene())
    game.register_scene("gameover", GameOverScene())
    game.register_scene("gamewin", GameWinScene())
    game.register_scene("outro", OutroScene())
    game.set_scene("menu")
    game.run()
