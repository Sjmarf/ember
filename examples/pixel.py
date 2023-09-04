# import ez_profile

import time
import inspect

start_time = time.time()
import pygame

print(f"Pygame import took {time.time()-start_time:.2f}s")

import logging

log = logging.getLogger("ember.size")
log.setLevel(logging.DEBUG)
log.addHandler(logging.FileHandler("log.log", "w+"))

import os
import sys

os.chdir(__file__.replace("pixel.py", ""))

start_time = time.time()
try:
    try:
        path = os.getcwd().replace(f"examples", "src")
        sys.path.append(path)
        print("PATH1", str(path))
        import ember  # noqa
    except ModuleNotFoundError:
        path = os.path.join(os.getcwd(), "src")
        sys.path.append(str(path))
        print("PATH2", str(path))
        import ember  # noqa
except RuntimeError as e:
    raise e.__cause__

print(f"Ember import took {time.time()-start_time:.2f}s")
pygame.init()

WIDTH = 801
HEIGHT = 600
ZOOM = 3

WIDTH += ZOOM - WIDTH % ZOOM
HEIGHT += ZOOM - WIDTH % ZOOM

screen = pygame.display.set_mode((WIDTH, HEIGHT))

display = pygame.Surface((WIDTH / ZOOM, HEIGHT / ZOOM), pygame.SRCALPHA)
clock = pygame.time.Clock()
ember.set_clock(clock)
ember.set_display_zoom(ZOOM)

wallpaper = pygame.image.load("wallpaper2.png").convert_alpha()
wallpaper2 = pygame.image.load("wallpaper2.png").convert_alpha()
image = pygame.image.load("image.png").convert_alpha()

ui = ember.style.PixelDark()

print(inspect.getmro(ui.Button))

with ember.View() as view:
    ui.HSwitch(size=(100, 50))

is_running = True

while is_running:
    _mouse = pygame.mouse.get_pos()
    mouse_pos = (_mouse[0] // ZOOM, _mouse[1] // ZOOM)

    for event in pygame.event.get():
        view.event(event)
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == ember.BUTTONDOWN:
            if event.element is play_button:
                with ember.animation.Spring(60, 1, 5):
                    stack.w = 150 if event.element.active else 100



        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                with ember.animation.EaseInOut(0.2):
                    button.w = 50

            elif event.key == pygame.K_a:
                with ember.animation.EaseInOut(0.2):
                    button.w = None

            elif event.key == pygame.K_y:
                fps.set_text("One fish, two fish, red fish, blue fish")

            elif event.key == pygame.K_u:
                view.start_manual_update()

            elif event.key == pygame.K_i:
                print(text2.rect)

    display.fill(ui.background_color)
    view.update(display)
    screen.blit(pygame.transform.scale(display, (WIDTH, HEIGHT)), (0, 0))

    clock.tick(120)
    pygame.display.flip()

pygame.quit()
