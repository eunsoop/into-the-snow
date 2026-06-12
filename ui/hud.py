import math

import pygame

from core.effector import ShakeEffector
from core.fonts import Fonts
from entity.projectile import Bullet


def fire_weapon_at_mouse(layer, dt, bullet_speed=500, offset=16):
    layer.fire_cooldown_timer = max(0.0, layer.fire_cooldown_timer - dt)
    mouse_buttons = pygame.mouse.get_pressed()
    if mouse_buttons[0] and layer.fire_cooldown_timer <= 0.0:
        layer.fire_cooldown_timer = 0.12
        mx, my = pygame.mouse.get_pos()
        vp = layer.tilemap.viewpoint
        wx = mx - vp.x
        wy = my - vp.y
        dx = wx - layer.player.x
        dy = wy - layer.player.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx /= dist
            dy /= dist
        else:
            dx, dy = layer.player.facing
        b = Bullet(layer.player.x + dx * offset, layer.player.y + dy * offset, dx, dy, is_enemy=False)
        b.speed = bullet_speed
        layer.add_entity(b)
        layer.add_effector(ShakeEffector(duration=0.10, intensity=2.5))


def paint_debug_lines(surface, lines):
    font = Fonts.Jersey_10(20)
    y_offset = 20
    for line in lines:
        if line:
            surface.blit(font.render(line, True, (255, 255, 255)), (20, y_offset))
            y_offset += 22
