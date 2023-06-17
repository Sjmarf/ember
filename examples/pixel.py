import pygame
import os
import sys
import time
import logging

os.chdir(__file__.replace("pixel.py", ""))

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

pygame.init()

log = logging.getLogger("ember.material")
log.setLevel(logging.DEBUG)
log.addHandler(logging.FileHandler("log.log", "w+"))

WIDTH = 402
HEIGHT = 402
ZOOM = 3

screen = pygame.display.set_mode((WIDTH, HEIGHT))

ember.init()

start_time = time.time()
style = ember.style.load("pixel_dark")
print(f"Style load took {time.time() - start_time}s")

display = pygame.Surface((WIDTH / ZOOM, HEIGHT / ZOOM), pygame.SRCALPHA)
clock = pygame.time.Clock()
ember.set_clock(clock)
ember.set_display_zoom(ZOOM)

wallpaper = pygame.image.load("wallpaper3.png").convert_alpha()

image = pygame.image.load("image.png").convert_alpha()
# material = ember.material.StretchedSurface(image)


view = ember.View(
    ember.Resizable(
        ember.VStack(
            ember.Button("1",width=50),
            ember.Button("2", width=50, height=ember.FILL),
            ember.Button("3",width=50),
            spacing=5,
            size=ember.FILL,
        ),
        size=100,
        handles=[ember.LEFT, ember.RIGHT, ember.TOP, ember.BOTTOM],
        material=ember.material.AverageColor((0,0,10))
    )
)

n = 0

is_running = True

while is_running:
    _mouse = pygame.mouse.get_pos()
    mouse_pos = (_mouse[0] // ZOOM, _mouse[1] // ZOOM)

    for event in pygame.event.get():
        view.event(event)
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame.JOYDEVICEADDED:
            print("init", pygame.joystick.get_count())
            pygame.joystick.init()
            joystick = pygame.joystick.Joystick(0)
            ember.joysticks.append(joystick)

    display.fill(style["background_color"])
    # display.blit(wallpaper, (0,0))
    ember.update()
    view.update(display)

    screen.blit(pygame.transform.scale(display, (WIDTH, HEIGHT)), (0, 0))

    clock.tick(60)
    # fps.set_text(str(round(clock.get_fps())))
    pygame.display.flip()

pygame.quit()
