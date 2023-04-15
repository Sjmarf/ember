import pygame
import os
import sys

path = os.getcwd().replace(f"examples", "src")
sys.path.append(path)
import ember  # noqa

pygame.init()
ember.init()
#
# log = logging.getLogger("ember.size")
# log.setLevel(logging.DEBUG)
# log.addHandler(logging.FileHandler("log.log", "w+"))

ZOOM = 3

screen = pygame.display.set_mode((600, 600))
ember.style.load('stone')

display = pygame.Surface((600 / ZOOM, 600 / ZOOM), pygame.SRCALPHA)
clock = pygame.time.Clock()
ember.set_clock(clock)
ember.set_display_zoom(ZOOM)

text = ember.Text("Amet ex magna adipisicing esse dolore veniam nostrud excepteur est irure. "
                  "Et veniam enim laborum irure aute cupidatat nulla aliquip laboris ullamco "
                  "cupidatat. Fugiat ea magna irure tempor ullamco magna culpa quis proident. "
                  "Exercitation est minim id Lorem fugiat laborum amet.", align="left")

text.set_color("white")

text_field = ember.TextField(text, size=ember.FILL, multiline=True)

button = ember.Button("Test", width=ember.FILL)
view = ember.View(
    ember.VStack(
        text_field,
        button,
        size=ember.FILL * 0.8,
        spacing=5
    )
)

is_running = True

while is_running:
    for event in pygame.event.get():
        view.event(event)
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == ember.BUTTONCLICKED:
            text.set_align("center")

    display.fill((20, 20, 20))
    ember.update()
    view.update(display)

    # surf = view.element.element.style.material._cache.get(view.element.element)
    # if surf:
    #     surf.fill((255,0,0,100))
    #     display.blit(surf, (0,0))

    screen.blit(pygame.transform.scale(display, (600, 600)), (0, 0))

    clock.tick(60)
    pygame.display.flip()

pygame.quit()
