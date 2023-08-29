import pygame
import ember

pygame.init()
clock = pygame.time.Clock()
ember.set_clock(clock)

screen = pygame.display.set_mode((400, 400))

with ember.View() as view:
    with ember.VStack(size=(100, 300)):
        ember.Panel("magenta", size=(100, 100))
        ember.Panel("aqua", size=(100, 100))

running = True
while running:
    for event in pygame.event.get():
        view.event(event)
        if event.type == pygame.QUIT:
            running = False

    screen.fill("black")
    view.update(screen)

    clock.tick(60)
    pygame.display.flip()
pygame.quit()