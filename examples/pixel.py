import pygame
import os
import sys
import logging

os.chdir(__file__.replace("pixel.py", ""))

try:
    path = os.getcwd().replace(f"examples", "src")
    sys.path.append(path)
    print('PATH1', str(path))
    import ember  # noqa
except ModuleNotFoundError:
    path = os.path.join(os.getcwd(), "src")
    sys.path.append(str(path))
    print('PATH2', str(path))
    import ember  # noqa

pygame.init()

log = logging.getLogger("ember.size")
log.setLevel(logging.DEBUG)
log.addHandler(logging.FileHandler("log.log", "w+"))

ZOOM = 3

screen = pygame.display.set_mode((600, 600))

ember.init()
style = ember.style.load("pixel_dark")

display = pygame.Surface((600 / ZOOM, 600 / ZOOM), pygame.SRCALPHA)
clock = pygame.time.Clock()
ember.set_clock(clock)
ember.set_display_zoom(ZOOM)

wallpaper = pygame.image.load("wallpaper2.png").convert_alpha()

button = ember.Button("Button")
text_field = ember.TextField(
            "",
            prompt="Test",
            multiline=True,
            height = 40,
        )
toggle = ember.Toggle()
slider = ember.Slider()

view = ember.View(
    ember.VStack(
        button,
        text_field,
        toggle,
        slider
    )
)

is_running = True

while is_running:
    for event in pygame.event.get():
        view.event(event)
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == ember.BUTTONCLICKED:
            text_field.multiline = not text_field.multiline

    display.fill(style["background_color"])
    ember.update()
    view.update(display)

    screen.blit(pygame.transform.scale(display, (600, 600)), (0, 0))

    clock.tick(60)
    pygame.display.flip()

pygame.quit()
