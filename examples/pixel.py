import pygame
import ember

pygame.init()
ember.init()
ember.style.load()

screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()

ember.set_clock(clock)

view = ember.View(
    ember.Button("Hello world")
)

is_running = True

while is_running:

    for event in pygame.event.get():
        view.event(event)
        if event.type == pygame.QUIT:
            is_running = False

    screen.fill((0,0,0))
    ember.update()
    view.update(screen)

    clock.tick(60)
    pygame.display.flip()

pygame.quit()
