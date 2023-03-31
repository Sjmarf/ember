import pygame
import os
import sys

try:
    import ember
except ModuleNotFoundError:
    path = os.getcwd().replace(f"examples", "")
    sys.path.append(path)
    import ember

pygame.init()
screen = pygame.display.set_mode((800,800))
display = pygame.Surface((200,200))
clock = pygame.time.Clock()

ember.init(clock)
ember.set_display_zoom(4)
ember.style.load("stone")

view = ember.View(
    ember.VStack(
        ember.TextField("The quick brown fox jumped over the lazy dog.", size=(150, 60)),
        ember.TextField("Lorem ipsum dolor sit amet, consectetur adipiscing elit. ", size=(150, 60))
    )
)

while True:
    for event in pygame.event.get():
        view.event(event)

        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit(0)

    ember.update()
    display.fill((20,20,20))
    view.update(display)
    screen.blit(pygame.transform.scale(display, (800,800)), (0, 0))

    clock.tick(60)
    pygame.display.flip()
