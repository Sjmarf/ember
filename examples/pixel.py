# import ez_profile

import time

start_time = time.time()
import pygame

print(f"Pygame import took {time.time()-start_time:.2f}s")

import logging

log = logging.getLogger("ember.trait")
log.setLevel(logging.DEBUG)
log.addHandler(logging.FileHandler("log.log", "w+"))

import os
import inspect
import sys


os.chdir(__file__.replace("pixel.py", ""))

start_time = time.time()
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

with ember.View() as view:
    with ember.VStack(content_w=50) as stack:
        button = ui.Button("hello")
        ui.Button("world")
        ember.Button(ui.Text("Hi"))

is_running = True

while is_running:
    _mouse = pygame.mouse.get_pos()
    mouse_pos = (_mouse[0] // ZOOM, _mouse[1] // ZOOM)

    for event in pygame.event.get():
        view.event(event)
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == ember.BUTTONDOWN:
            with ember.animation.EaseOut(1):
                stack.content_w = ember.size.AbsoluteSize(120)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                with ember.animation.Linear(1):
                    stack.set_w(200)

            elif event.key == pygame.K_a:
                with ember.animation.EaseOut(1):
                    stack.set_w(100)

            elif event.key == pygame.K_y:
                fps.set_text("One fish, two fish, red fish, blue fish")

            elif event.key == pygame.K_u:
                print(text.rect)

            elif event.key == pygame.K_i:
                print(text2.rect)

    display.fill("gray8")
    # display.blit(wallpaper, (0,0))
    ember.update()
    # start_time = time.time()
    view.update(display)
    # print(f"1/{round(1/(time.time()-start_time))}s")
    screen.blit(pygame.transform.scale(display, (WIDTH, HEIGHT)), (0, 0))

    clock.tick(120)
    # text.set_text(f"{float(clock.get_fps()): .0f}")

    # fps.set_text(str(round(clock.get_fps())))
    # for button,text in zip(buttons,size_texts):
    #     text.set_text(f"{button.rect.x}, {button.rect.w}")
    pygame.display.flip()

pygame.quit()
