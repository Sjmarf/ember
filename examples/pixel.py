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

log = logging.getLogger("ember.size")
log.setLevel(logging.DEBUG)
log.addHandler(logging.FileHandler("log.log", "w+"))

WIDTH = 400
HEIGHT = 400
ZOOM = 3

WIDTH += ZOOM - WIDTH % ZOOM
HEIGHT += ZOOM - WIDTH % ZOOM

screen = pygame.display.set_mode((WIDTH, HEIGHT))  

ember.init()

start_time = time.time()
style = ember.style.load("pixel_dark")
print(f"Style load took {time.time() - start_time}s")

display = pygame.Surface((WIDTH / ZOOM, HEIGHT / ZOOM), pygame.SRCALPHA)
clock = pygame.time.Clock()
ember.set_clock(clock)
ember.set_display_zoom(ZOOM)

wallpaper = pygame.image.load("wallpaper2.png").convert_alpha()
wallpaper2 = pygame.image.load("wallpaper2.png").convert_alpha()
image = pygame.image.load("image.png").convert_alpha()


font = ember.PixelFont(
    "font.png",
    characters=" abcdefghijklmnopqrstuvwxyz",
    character_padding=(1, 1),
)

with ember.View() as view:
    with ember.VStack():
        with ember.VScroll(size=ember.FILL):
            ember.Box(size=(ember.FILL, 499), material=ember.material.StretchedSurface("image.png"))
        fps = ember.Text()
       
        
    # ember.TextField("Hello world")

#view = ember.View(ember.Button())

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

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_k:
                view[0].start_manual_update()

            elif event.key == pygame.K_a:
                with ember.animation.Linear(0.1):
                    element.set_h(100)

            elif event.key == pygame.K_s:
                with ember.animation.Linear(0.1):
                    element.set_h(60)

            elif event.key == pygame.K_u:
                view.start_manual_update()

        if event.type == ember.BUTTONCLICKED:
            pass
            # text.set_material(ember.material.Color("red"))
            # icon.set_material(ember.material.AverageColor((0,0,50)))
            # icon.set_icon("triangle_right" if icon.name == "pause" else "pause")

    display.fill(style["background_color"])
    # display.blit(wallpaper, (0,0))
    ember.update()
    view.update(display)

    screen.blit(pygame.transform.scale(display, (WIDTH, HEIGHT)), (0, 0))

    clock.tick(60)

    fps.set_text(str(round(clock.get_fps())))
    # for button,text in zip(buttons,size_texts):
    #     text.set_text(f"{button.rect.x}, {button.rect.w}")
    pygame.display.flip()

pygame.quit()