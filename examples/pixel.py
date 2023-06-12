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

log = logging.getLogger("ember.nav")
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

ember.default_styles.get(ember.ViewLayer).listen_for_exit = True

display = pygame.Surface((WIDTH / ZOOM, HEIGHT / ZOOM), pygame.SRCALPHA)
clock = pygame.time.Clock()
ember.set_clock(clock)
ember.set_display_zoom(ZOOM)

wallpaper = pygame.image.load("wallpaper3.png").convert_alpha()

red_button = ember.ButtonStyle(
    default_material=ember.material.Color("red")
)

fps = ember.Text("")

view = ember.View(
    ember.VStack(
        ember.Text("Hello"),
        ember.Text("World")
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
    #display.blit(wallpaper, (0,0))
    ember.update()
    view.update(display)

    screen.blit(pygame.transform.scale(display, (WIDTH, HEIGHT)), (0, 0))

    clock.tick(60)
    #fps.set_text(str(round(clock.get_fps())))
    pygame.display.flip()

pygame.quit()
