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

# log = logging.getLogger("ember.size")
# log.setLevel(logging.DEBUG)
# log.addHandler(logging.FileHandler("log.log", "w+"))

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
# material = ember.material.StretchedSurface(image)

font = ember.PixelFont(
    "font.png",
    characters=" abcdefghijklmnopqrstuvwxyz",
    character_padding=(1, 1),
)
### font = ember.Font("comicsans", 50, antialias=True)
# text_style = ember.TextStyle(font=font)

# ember.default_styles.text.material = ember.material.Color("black")
# ember.default_styles.text.secondary_material = ember.material.Color("cyan")

ember.default_styles.icon.secondary_material = ember.material.Color("indianred")
ember.default_styles.icon.tertiary_material = ember.material.Color("blue", alpha=100)

text = ember.Text("")
stack = ember.VStack([ember.Button(str(i), w=50, h=ember.FILL) for i in range(3)], h=ember.FILL)

resizable = ember.Resizable(
            stack,
            size=(50, 50),
            handles=[ember.TOP, ember.BOTTOM, ember.LEFT, ember.RIGHT],
            material=ember.material.Color("indianred")
        )

view = ember.View(
    resizable,
    keyboard_nav=False
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

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                resizable.set_w(resizable.rect.w - 1)
            elif event.key == pygame.K_RIGHT:
                resizable.set_w(resizable.rect.w + 1)

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
    text.set_text(f"{stack.rect.x}, {stack.rect.w}")
    text.set_color("lime" if all(x.rect.w == stack[0].rect.w for x in stack) else "white")
    # fps.set_text(str(round(clock.get_fps())))
    # for button,text in zip(buttons,size_texts):
    #     text.set_text(f"{button.rect.x}, {button.rect.w}")
    pygame.display.flip()

pygame.quit()
