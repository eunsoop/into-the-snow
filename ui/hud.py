import math

import pygame

from core.effector import ShakeEffector
from core.fonts import Fonts
from entity.projectile import Bullet

def fire_weapon_at_mouse(layer, dt, bullet_speed=500, offset=16):
    """
    Handle weapon firing mechanics. Reads player mouse input to shoot bullets in
    the direction of the mouse pointer, updating bullet speed, screen shake, and fire rate cooldown.
    
    :param layer: The current GameLayer instance containing player and entities
    :param dt: Delta time in seconds
    :param bullet_speed: Velocity of the spawned bullet (default 500)
    :param offset: Pixel distance from player center to spawn bullet (default 16)
    """

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
    """
    Render a list of debug information strings onto the top-left corner of the screen.
    
    :param surface: The destination drawing Surface
    :param lines: List of string lines to draw
    """
    font = Fonts.Jersey_10(20)
    y_offset = 20
    for line in lines:
        if line:
            surface.blit(font.render(line, True, (255, 255, 255)), (20, y_offset))
            y_offset += 22

