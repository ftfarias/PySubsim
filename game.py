"""
Submarine game - multi-window framework
Author: Ftfarias
"""

from __future__ import annotations
import sys, math, time, random
from pygame._sdl2 import Texture
from pygame._sdl2 import Window, Renderer  # requires pygame >= 2.5
import pygame
from button import Button   
from const import *
from submarine import Submarine

pygame.init()
CLOCK = pygame.time.Clock()
FPS   = 60

# ---------------------------------------------------------------------------
# Helper drawing routines
# ---------------------------------------------------------------------------
def draw_sonar(renderer: pygame.Surface | Renderer, t: float, size: tuple[int, int]):
    w, h = size
    cx, cy = w // 2, h // 2
    radius = min(cx, cy) - 10
    color_bg = (5, 15, 25)
    color_grid = (20, 60, 90)
    color_beam = (0, 200, 0)
    color_ping = (0, 150, 0)

    surf = pygame.Surface(size)
    surf.fill(color_bg)

    # range rings
    for r in range(4):
        pygame.draw.circle(surf, color_grid, (cx, cy), (r + 1) * radius // 4, 1)

    # sweeping beam
    angle = (t * 20) % 360           # 90° per second
    rad = math.radians(angle)
    x = cx + radius * math.cos(rad)
    y = cy - radius * math.sin(rad)
    pygame.draw.line(surf, color_beam, (cx, cy), (x, y), 3)

    # # fake random pings
    # for _ in range(8):
    #     pr = random.random() * radius
    #     pa = random.random() * 2 * math.pi
    #     px = cx + pr * math.cos(pa)
    #     py = cy - pr * math.sin(pa)
    #     pygame.draw.circle(surf, color_ping, (px, py), 2)

    _blit(renderer, surf, (0, 0))


def draw_map(renderer: pygame.Surface | Renderer, size: tuple[int, int], submarine: Submarine):
    w, h = size
    surf = pygame.Surface(size)
    surf.fill((0, 30, 60))
    grid_color = (0, 80, 120)
    for x in range(0, w, 40):
        pygame.draw.line(surf, grid_color, (x, 0), (x, h))
    for y in range(0, h, 40):
        pygame.draw.line(surf, grid_color, (0, y), (w, y))

    # placeholder sub position
    pygame.draw.circle(surf, (230, 230, 0), (w // 2, h // 2), 6)

    _blit(renderer, surf, (0, 0))


def create_button(surf: pygame.Surface, 
                  rect: pygame.Rect, 
                  label: str, 
                  color1:tuple=(70, 70, 200), 
                  color2:tuple=(255, 255, 255)):
    """Create a button on the given surface."""
    pygame.draw.rect(surf, color1, rect, border_radius=6)  # Button background
    pygame.draw.rect(surf, color2, rect, 2, border_radius=6)  # Button border
    font = pygame.font.SysFont("consolas", 15)
    btn_lbl = font.render(label, True, color2)
    surf.blit(btn_lbl, (rect.x + (rect.width - btn_lbl.get_width()) // 2,
                        rect.y + (rect.height - btn_lbl.get_height()) // 2))  # Center text in the button

def draw_controls(renderer: pygame.Surface | Renderer, size: tuple[int, int]):
    surf = pygame.Surface(size)
    surf.fill((30, 30, 30))
    font = pygame.font.SysFont("consolas", 15)

    # Throttle label and bar
    lbl = font.render("Throttle:", True, (200, 200, 200))
    surf.blit(lbl, (10, 10))
    pygame.draw.rect(surf, (80, 80, 80), pygame.Rect(110, 14, 200, 12), border_radius=6)
    pygame.draw.rect(surf, (0, 180, 0), pygame.Rect(110, 14, submarine.throttle_pct * 2, 12), border_radius=6)

    # Speed label
    btn = Button(
        text="Speed",
        x=10,
        y=50,
        width=100,
        height=30,
        command=lambda x: print("Speed button clicked!"),
        additional_data=["Speed"],
        color=(255, 255, 255)
    )

    # Button
    # button_rect = pygame.Rect(10, 50, 100, 30)  # x, y, width, height
    # create_button(surf, button_rect, "Click Me")

    # pygame.draw.rect(surf, (70, 70, 200), button_rect, border_radius=6)  # Button background
    # pygame.draw.rect(surf, (255, 255, 255), button_rect, 2, border_radius=6)  # Button border
    # btn_lbl = font.render("Click Me", True, (255, 255, 255))
    # surf.blit(btn_lbl, (button_rect.x + 10, button_rect.y + 5))  # Center text in the button
    btn.draw(surf)  # Draw the button on the surface

    _blit(renderer, surf, (0, 0))
    # return {'t':button_rect} # return a dict with the button rect for interaction
    return [btn] # return a dict with the button rect for interaction
    

def _blit(renderer: pygame.Surface | pygame._sdl2.Renderer,
          surf: pygame.Surface,
          pos):
    # ➊ create a texture from the surface
    tex = Texture.from_surface(renderer, surf)

    # ➋ copy it to the renderer at the desired position (= dstrect)
    x, y = pos
    w, h = surf.get_size()
    renderer.blit(tex, pygame.rect.Rect(x, y, w, h))

# ---------------------------------------------------------------------------
# Submarine game main class
# ---------------------------------------------------------------------------

submarine = Submarine()



# ---------------------------------------------------------------------------
# MULTI-WINDOW VERSION
# ---------------------------------------------------------------------------
class MultiWindowApp:

    def __init__(self):
        self.win_sonar  = Window("Sonar",    size=(400, 400), position=(  0,   0), resizable=True)
        self.win_map    = Window("Map",      size=(400, 400), position=(410,   0), resizable=True)
        self.win_ctrl   = Window("Controls", size=(400, 200), position=(  0, 500), resizable=True)

        self.rend_sonar = Renderer(self.win_sonar)
        self.rend_map   = Renderer(self.win_map)
        self.rend_ctrl  = Renderer(self.win_ctrl)

    def run(self):
        start_time = time.perf_counter()
        running = True
        while running:
            t = time.perf_counter() - start_time
            # Update submarine state
            submarine.step(1.0 / FPS)  # Simulate a step for the submarine
            controls = []

            # --- drawing ---
            draw_sonar(self.rend_sonar, t, self.win_sonar.size)
            self.rend_sonar.present()  # Ensure the sonar window updates

            draw_map(self.rend_map, self.win_map.size, submarine)
            self.rend_map.present()  # Ensure the map window updates

            new_controls = draw_controls(self.rend_ctrl, self.win_ctrl.size)
            controls.extend(new_controls)  # Update controls with new buttons
            self.rend_ctrl.present()  # Ensure the controls window updates
            # --- end drawing ---
            for event in pygame.event.get():
                for control in controls:
                    control.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pass
                    # if controls['t'].collidepoint(event.pos):
                    #     print("Button clicked!")  # Handle button click here
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print('Escape')
                        running = False
                    elif event.key == pygame.K_UP:
                        print('Up')
                    elif event.key == pygame.K_DOWN:
                        print('Down')
                    elif event.key == pygame.K_LEFT:
                        print('Left')
                    elif event.key == pygame.K_RIGHT:
                        print('Right')
                    elif event.key == pygame.K_EQUALS:
                        submarine.throttle_pct += 5
                    elif event.key == pygame.K_MINUS:
                        submarine.throttle_pct -= 5
            CLOCK.tick(FPS)

        pygame.quit()
        sys.exit()


# ---------------------------------------------------------------------------
# Boot strap
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    MultiWindowApp().run()
